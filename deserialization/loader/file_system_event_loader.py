from deserialization.loader.event_loader import EventLoader


class FileSystemEventLoader(EventLoader):

    def load_event(self, league, event_type, event_params):
        pass

    def load_all_events(self, league, event_type, event_params):
        pass

    def load_event_by_date(self, league, event_type, event_params, timestamp):
        pass

