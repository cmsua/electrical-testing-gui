# Hexaboard Electrical Testing GUI
## University of Alabama

## Installation

This repository is designed to install from source.

Python 3.10 or above is required for this program due to using `type | None` sytnax.

```bash
# Clone the Repository
git clone https://github.com/cmsua//electrical-testing-gui.git
cd hexaboard-gui

# Setup a Virtual Environment
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
```

## Developer Reference Guide
### Design

In this interface, the minimum actionable unit is defined as a **Test Step**, which represents one "action" taken on the test environment, such as enabling power supply, scanning barcodes, or prompting the user to connect two components. Each test step is organized sequentially into a **Test Stage**, which is an ordered list of test steps. Three stages, **Setup**, **Runtime**, and **Shutdown** are then organized into one **Test Flow**.

Programmatically, a test step is a custom python object designed to act as the connection between the user-facing GUI elements and the code that directly acts upon the board. Any test step contains a `create_widget` method, which is called at when the user advances to said step, and then immediately displayed on-screen. Passed to this method is a `data` object, which contains output from previous steps. The method should return a `TestWidget`, a custom subclass of `QWidget` containing three signals: `finished`, `crashed`, and `advance`.

The `finished` and `crashed` signals are designed to be emitted after the test step has completed any important code, such as power control. In particular, it is assumed that when `finished` or `crashed` are emitted, the widget is from that moment on, read-only. It is important to note that the two signals are mutually-exclusive; if a widget emits one, it should not emit the other. **The `finished` signal should still be emitted in the event of a failed test. `crashed` should only be emitted if the setup is unrecoverable.**

When the `finished` signal is recieved with an object as a paramater, said object is saved to `data[step.get_data_field()]`, which is then passed to future step's `create_widget` function. The user-interface will then queue the next test step in the current phase, or if there is none, queue the next step in the immediately-following phase.

If the `crashed` signal is recieved instead, it is assumed the test has failed beyond repair. An error message is required for logging, however no data is saved to be passed to future tests. If the test stage is Setup or Runtime, the interface will immediately queue the first step in the Shutdown phase. If the current phase is Shutdown, the interface will queue a restart from the  first step of the Setup phase.

The `advance` signal is a control signal. When `finished` and `crashed` are outputted, the widget is still displayed in the event that the user wishes to view the stage's output, if there is any. The `advance` signal should be emitted when the user opts to continue to the next test step, with data as a string for the reason (user input/automatic continuation).

Additionally, each test step contains three additional methods: `step.get_name() -> str`, for use in the debug logs as well as the LED status indicators on the left, `get_output_count() -> int`, to indicate how many output LEDs the step controls, and `get_output_status(in_data, out_data) -> list[str]`. This final method should return an array of strings with a length of `get_output_count()`, each directly correlating to an output LED's color. The data passed to this function is the same data emitted in the `finished` signal. Valid colors are listed in `misc_widgets.py`.

### Pre-provided Steps

#### steps.input_steps.DisplayStep

A foundational step, this will create a widget with a text message, optional image, and a continue button. No imput is collected.

#### steps.input_steps.SelectStep

This will create a widget with a dropdown menu, of which the user is expected to pick one item. A "select" button is included for confirmation and advancement.

#### steps.input_steps.VerifyStep

A step that accepts a list of yes/no questions, a message, and an optional image. If the step is flagged critical, all questions must be answered 'yes' or an error will be emitted. Otherwise, if a question is answered no, the test will not emit an error, but flag the data as yellow.

#### steps.thread_steps.ThreadStep

An abstract class, which displays a message. Upon widget creation, the class's abstract method `create_thread(data) -> QThread` is called and immediately started. The thread has three signals: the default `finished` signal, `crashed`, and `data`. If the thread's `crashed` or `data` methods are called and recieved by the step's widget, it will immediately forward them onwards. As some threads may need time to wrap-up, the advacement button will not be enabled until `finished` is emitted by the thread.

This class supports auto-advancement, on which `advance` will be emitted by the widget as soon as the thread emits `finished`. It also supports an Abort Thread button, which will terminate the thread, emit `crashed`, and unlock the advancement button. Lastly, the step supports an automatic timeout in seconds, after which the task will act as if the abort button has been pressed.

#### steps.thread_steps.DynamicThreadStep

A wrapper for `steps.thread_steps.ThreadStep`, this step accepts a method reference in its constructor. The thread created by the defined `create_thread` method will simply call this provided method, emit `data` with the returned result, and `crashed` if an exception is raised inside the method.