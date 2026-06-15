from django.apps import AppConfig


class TrackzenConfig(AppConfig):
    name = 'TrackZen'
    
    def ready(self):
        import TrackZen.signals
