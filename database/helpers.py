from .async_saver import DBSaver


class SaveAsyncMixin:
    def save_async(self):
        model_name = self.__class__.__name__
        dbsaver = DBSaver()
        model_attr = dbsaver.model_attr
        publisher = dbsaver.get_json_publisher()
        send_data = self.__dict__
        send_data.pop('_state')
        send_data[model_attr] = model_name
        publisher.send_message(self.__dict__)