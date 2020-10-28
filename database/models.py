import os
import collections
import uuid

import requests
from django.contrib.postgres.fields import ArrayField
from django.db import models, transaction
from django.conf import settings

from painter import Painter
from painter.base import MaxHeightException
from promo_bots.browser import CheckpointChallenger, PhotoUploader
from promo_bots.counters import IgLogFollowingsCounter, IgLogUnfollowingsCounter, IgLogLikeCounter, IgLogLookingCounter
from .helpers import SaveAsyncMixin
from .exceptions import OldContentDownloadError


class PromoType:
    following = 1
    unfollowing = 2
    liking = 3
    looking = 4
    choices = (
        (following, following),
        (unfollowing, unfollowing),
        (liking, liking),
        (looking, looking),
    )
    verbose = {
        following: 'following',
        unfollowing: 'unfollowing',
        liking: 'liking',
        looking: 'looking',
    }
    limits = {
        following: 500,
        unfollowing: 1000,
        liking: 700,
        looking: 1000,
    }
    counters = {
        following: IgLogFollowingsCounter,
        unfollowing: IgLogUnfollowingsCounter,
        liking: IgLogLikeCounter,
        looking: IgLogLookingCounter,
    }
    human = {
        following: 'Фолловинг',
        unfollowing: 'Анфолловинг',
        liking: 'Лайкинг',
        looking: 'Лукинг',
    }

    @classmethod
    def get_verbose(cls, promo_type):
        return cls.verbose[promo_type]

    @classmethod
    def get_limit(cls, promo_type):
        return cls.limits[promo_type]

    @classmethod
    def get_counter_cls(cls, promo_type):
        return cls.counters[promo_type]

    @classmethod
    def get_human(cls, promo_type):
        return cls.human[promo_type]


class Proxy(models.Model):
    ip = models.GenericIPAddressField()
    port = models.IntegerField()
    username = models.CharField(max_length=1024, null=True, blank=True)
    password = models.CharField(max_length=1024, null=True, blank=True)
    enable = models.BooleanField(default=True)

    class Meta:
        db_table = 'proxy'


class ExternalProxy(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    uid = models.CharField(max_length=1024, null=True, blank=True)
    host = models.CharField(max_length=1024)
    port = models.PositiveIntegerField()
    username = models.CharField(max_length=1024, null=True, blank=True)
    password = models.CharField(max_length=1024, null=True, blank=True)
    ip = models.GenericIPAddressField()
    country = models.CharField(max_length=1024)
    active = models.BooleanField()
    ended = models.DateTimeField()
    proxy = models.ForeignKey(Proxy, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        db_table = 'external_proxy'


class Accounts(models.Model):
    username = models.CharField(max_length=4096)
    password = models.CharField(max_length=128)
    email = models.EmailField(max_length=4096)
    email_password = models.CharField(max_length=4096)
    fb_email = models.EmailField(max_length=4096, null=True, blank=True)
    fb_pass = models.CharField(max_length=4096, null=True, blank=True)
    banned = models.BooleanField(default=False)
    phone = models.CharField(max_length=64, null=True, blank=True)
    proxy = models.ForeignKey(Proxy, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        db_table = 'account'

    def get_new_cookies(self):
        login_cookies, phone = CheckpointChallenger(
            self.username,
            self.password,
            self.email,
            self.email_password,
            proxy_ip=self.proxy.ip if self.proxy else None,
            proxy_port=self.proxy.port if self.proxy else None,
        ).challenge()
        if phone:
            self.phone = phone
            self.save()
        return login_cookies

    def get_bot_client(self, log_func=None):
        from promo_bots.client import IgClient
        return IgClient(
            self.username,
            self.password,
            self.email,
            self.email_password,
            account_id=self.id,
            proxy_ip=self.proxy.ip if self.proxy else None,
            proxy_port=self.proxy.port if self.proxy else None,
            log_func=log_func
        )

    def get_uploader(self):
        return PhotoUploader(
            self.username,
            self.password,
            self.fb_email,
            self.fb_pass,
            proxy_ip=self.proxy.ip,
            proxy_port=self.proxy.port
        )


class Profile(models.Model, SaveAsyncMixin):
    instagram_id = models.BigIntegerField(db_index=True, unique=True)
    username = models.CharField(max_length=1024, blank=True)
    full_name = models.CharField(max_length=1024, blank=True, default='')
    is_private = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    profile_pic_url = models.URLField(blank=True, default='', max_length=4096)
    profile_pic_url_hd = models.CharField(max_length=1024, default='', blank=True, null=True)
    media_count = models.PositiveIntegerField(db_index=True, null=True)
    follower_count = models.PositiveIntegerField(null=True)
    following_count = models.PositiveIntegerField(null=True)
    biography = models.TextField(blank=True, null=True, default='')
    external_url = models.URLField(null=True, blank=True, max_length=4096)
    last_media_id = models.CharField(max_length=1024, null=True, blank=True)
    last_media_pud_date = models.DateTimeField(null=True, blank=True)

    owner = models.ForeignKey(Accounts, null=True, blank=True, on_delete=models.SET_NULL)
    came_from_name = models.CharField(max_length=1024)
    came_from_id = models.CharField(max_length=1024)

    promo_type = models.PositiveIntegerField(choices=PromoType.choices, null=True, blank=True, db_index=True)
    passed = models.BooleanField(default=False)

    class Meta:
        db_table = 'profile'


class Following(models.Model, SaveAsyncMixin):
    Status = collections.namedtuple('Status', ['code', 'name'])
    Unfollow = Status(code=0, name='unfollow')
    Follow = Status(code=1, name='follow')
    Processed = Status(code=2, name='processed')
    NotFound = Status(code=3, name='not_found')
    Requested = Status(code=4, name='requested')
    Unrequested = Status(code=5, name='unrequested')
    Block = Status(code=6, name='block')
    Unblock = Status(code=7, name='unblock')
    Deleted = Status(code=8, name='user_deleted')
    AllStatuses = [Unfollow, Follow, Processed, NotFound, Requested, Unrequested, Block, Unblock, Deleted]

    opened = models.DateTimeField(auto_now_add=True, db_index=True)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    owner = models.ForeignKey(Accounts, on_delete=models.CASCADE)
    status = models.PositiveIntegerField(choices=AllStatuses, db_index=True)
    closed = models.DateTimeField(null=True, db_index=True)

    class Meta:
        unique_together = ('profile', 'owner')
        db_table = 'followed'


class Liked(models.Model, SaveAsyncMixin):
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    owner = models.ForeignKey(Accounts, on_delete=models.CASCADE)
    picture_id = models.CharField(max_length=1024, null=True, blank=True)

    class Meta:
        unique_together = ('profile', 'owner', 'picture_id')
        db_table = 'liked'


class Looked(models.Model, SaveAsyncMixin):
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    owner = models.ForeignKey(Accounts, on_delete=models.CASCADE)
    items_ids = ArrayField(models.CharField(max_length=1024), blank=True, null=True)

    class Meta:
        db_table = 'looked'


class Ignored(models.Model, SaveAsyncMixin):
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    owner = models.ForeignKey(Accounts, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    reason = models.TextField(null=True, blank=True)

    class Meta:
        unique_together = ('profile', 'owner')
        db_table = 'ignored'


class Posted(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    account = models.ForeignKey(Accounts, on_delete=models.SET_NULL, null=True, blank=True)
    instagram_id = models.CharField(max_length=1024)
    url = models.URLField(max_length=1024)

    class Meta:
        db_table = 'posted'


class TextContent(models.Model):
    added = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(Accounts, null=True, blank=True, on_delete=models.SET_NULL)
    parser_name = models.CharField(max_length=1024)
    text = models.TextField()
    post_id = models.CharField(max_length=1024)
    image = models.CharField(max_length=1024, null=True, blank=True)
    approved = models.BooleanField(null=True, default=None)
    uploaded = models.NullBooleanField()
    instagram_post = models.ForeignKey(Posted, on_delete=models.SET_NULL, null=True, blank=True)
    ignore = models.BooleanField(default=False)

    class Meta:
        db_table = 'text_content'

    def draw(self, painter: Painter):
        filename = f'{self.id}.jpg'
        try:
            self.image = painter.draw_picture(self.text, filename).replace(settings.IMAGES_DIR + os.sep, '')
        except MaxHeightException:
            self.ignore = True
            image_path = None
        else:
            image_path = self.image_path
        self.save()
        return image_path

    @property
    def image_path(self):
        return os.path.join(settings.IMAGES_DIR, self.image) if self.image else None

    def upload(self, client, painter, caption=''):
        if self.image_path is None or not os.path.exists(self.image_path):
            image_path = self.draw(painter)
            if image_path is None:
                return None
        media = client.upload_photo(self.image_path, caption=caption)['media']
        url = media['image_versions2']['candidates'][0]['url']
        new_post = Posted(account=self.owner, instagram_id=media['id'], url=url)
        new_post.save()
        self.instagram_post = new_post
        self.save()
        return media['id']


class ApprovedChat(models.Model):
    added = models.DateTimeField(auto_now_add=True)
    chat = models.CharField(max_length=1024, unique=True)
    enabled = models.BooleanField(default=False)

    class Meta:
        db_table = 'approved_chat'


class IgLog(models.Model, SaveAsyncMixin):
    account = models.ForeignKey(Accounts, on_delete=models.CASCADE)
    url = models.URLField(max_length=1024, db_index=True)
    request_time = models.DateTimeField(db_index=True)
    request_method = models.CharField(max_length=1024)
    request_headers = models.TextField()
    request_body = models.TextField(null=True)
    response_time = models.DateTimeField(null=True)
    status_code = models.PositiveIntegerField(null=True, db_index=True)
    response_headers = models.TextField(null=True)
    response_body = models.TextField(null=True)
    error = models.TextField(null=True)

    class Meta:
        db_table = 'ig_log'


class IgStat(models.Model, SaveAsyncMixin):
    account = models.ForeignKey(Accounts, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    followers_count = models.BigIntegerField()
    following_count = models.BigIntegerField()

    class Meta:
        db_table = 'ig_stat'


class SourceProfile(models.Model):
    added = models.DateTimeField(auto_now_add=True)
    username = models.CharField(max_length=1024)
    instagram_id = models.BigIntegerField(db_index=True, unique=True)

    class Meta:
        db_table = 'source_profile'


class ParsingHistory(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    ended = models.DateTimeField(null=True, blank=True)
    process_id = models.PositiveIntegerField(null=True, blank=True)
    account = models.ForeignKey(Accounts, null=True, blank=True, on_delete=models.SET_NULL)
    source_profile = models.ForeignKey(SourceProfile, on_delete=models.CASCADE)
    saved_cnt = models.IntegerField(null=True, blank=True)
    skiped_cnt = models.IntegerField(null=True, blank=True)
    traceback = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'parsing_history'


class PromoHistory(models.Model):
    start = models.DateTimeField(auto_now_add=True)
    end = models.DateTimeField(null=True, blank=True)
    process_id = models.PositiveIntegerField(null=True, blank=True)
    promo_type = models.PositiveIntegerField(choices=PromoType.choices)
    account = models.ForeignKey(Accounts, on_delete=models.CASCADE)
    success = models.NullBooleanField()
    traceback = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'promo_history'


class OldPost(models.Model):
    ig_id = models.CharField(max_length=1024)
    created = models.DateField(auto_now_add=True)
    taken_at = models.BigIntegerField()
    owner = models.ForeignKey(Accounts, on_delete=models.CASCADE)
    media_type = models.PositiveIntegerField()
    code = models.CharField(max_length=1024)
    comment_count = models.PositiveIntegerField()
    like_count = models.PositiveIntegerField()
    url = models.URLField(max_length=4096)
    image_name = models.CharField(max_length=4096, null=True, blank=True)
    text_content = models.OneToOneField(TextContent, null=True, blank=True, on_delete=models.SET_NULL)

    def get_full_path(self):
        save_folder = os.path.normpath(os.path.abspath(os.path.join(settings.BASE_DIR, 'images')))
        return os.path.join(save_folder, self.image_name)

    @property
    @transaction.atomic
    def image_path(self):
        if self.image_name:
            return self.get_full_path()
        self.image_name = "old_post_" + str(uuid.uuid4())
        self.download_image(self.get_full_path())
        self.save()
        return self.get_full_path()

    def download_image(self, save_path):
        response = requests.get(self.url, stream=True)
        if response.status_code != 200:
            raise OldContentDownloadError("Old post downloader error: response != 200")
        with open(save_path, 'wb') as f_obj:
            for chunk in response:
                f_obj.write(chunk)

    class Meta:
        db_table = 'old_post'


class SimonlineTransaction(models.Model, SaveAsyncMixin):
    created = models.DateTimeField(auto_now_add=True)
    owner_username = models.CharField(max_length=1024, null=True, blank=True)
    tzid = models.CharField(max_length=1024)
    country_code = models.PositiveIntegerField()
    phone = models.CharField(max_length=1024)
    sms_code = models.CharField(max_length=1024, null=True, blank=True)
    sms_code_timestamp = models.DateTimeField(null=True, blank=True)
    confirmed_timestamp = models.DateTimeField(null=True, blank=True)
    getting_attempts = models.PositiveIntegerField(default=0)
    success = models.NullBooleanField(default=None)

    class Meta:
        db_table = 'simonline_transaction'


class MediaLiker(models.Model, SaveAsyncMixin):
    user_ig_id = models.BigIntegerField()
    user_username = models.CharField(max_length=1024)
    user_full_name = models.CharField(max_length=1024)
    user_is_private = models.BooleanField()
    user_profile_pic_url = models.URLField(max_length=4094)
    
    media_ig_id = models.CharField(max_length=1024)
    media_code = models.CharField(max_length=1024)
    media_taken_at = models.DateTimeField()
    media_caption = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'media_likers'


class MediaComments(models.Model, SaveAsyncMixin):
    ig_id = models.BigIntegerField()
    text = models.TextField()
    created_at = models.DateTimeField()
    like_count = models.IntegerField()

    user_ig_id = models.BigIntegerField()
    user_username = models.CharField(max_length=1024)
    user_full_name = models.CharField(max_length=1024)
    user_is_private = models.BooleanField()
    user_profile_pic_url = models.URLField(max_length=4094)

    media_ig_id = models.CharField(max_length=1024)
    media_code = models.CharField(max_length=1024)
    media_taken_at = models.DateTimeField()
    media_caption = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'media_comments'
