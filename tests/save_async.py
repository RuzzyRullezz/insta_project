import bootstrap
bootstrap.setup()

from database.models import Profile

if __name__ == '__main__':
    profile = Profile.objects.first()
    profile.passed = True
    profile.save_async()
