## Testing area for PyQt

To test out PyQt-related things in isolation, we can just spin up a regular instance of a PyQt app and add our widgets and components to the `test_view.py`.

To do this simply run (in the root of the project):

    python main.py

Bear in mind that any widgets or component that attempts to use the `iface` present in qgis will fail, since that interface is not provided through the normal PyQt-app.