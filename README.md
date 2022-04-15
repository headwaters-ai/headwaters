# headwaters

Simple stream sources for event-driven application development.

### Install

From [Pypi](https://pypi.org/project/headwaters/):

After creating a virtual environment, on the cli:

```>>> pip install -U headwaters```

then start the default streaming server from the cli:

```>>> hw```

The CLI output shows the location of the server and ui.

Streams can be connected to at the server: http://127.0.0.1:5555/api/v0

To control the streams, use the ui running at http://127.0.0.1:5555/ui

Simple as that.

*While headwaters is running* you can see and adjust the behaviour of your stream:


- start and stop the stream;
- adjust the frequency of the events emitted by the stream;
- trigger a burst mode to send a flurry of events, with configurable frequency and volume.

:)