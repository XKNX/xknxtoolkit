from imgui_bundle import imgui, hello_imgui, imgui_node_editor as ed


class KnxGuiApp:
    def __init__(self) -> None:
        self._editor_context: ed.EditorContext | None = None

    def setup(self) -> None:
        config = ed.Config()
        self._editor_context = ed.create_editor(config)

    def shutdown(self) -> None:
        if self._editor_context:
            ed.destroy_editor(self._editor_context)
            self._editor_context = None

    def render(self) -> None:
        if not self._editor_context:
            return

        ed.set_current_editor(self._editor_context)
        ed.begin("KNX Node Editor", imgui.ImVec2(0, 0))

        node_id = ed.NodeId(1)
        ed.begin_node(node_id)
        imgui.begin_group()
        imgui.text("Test Device")
        imgui.text("1.1.1")
        imgui.end_group()

        imgui.spacing()

        ed.begin_pin(ed.PinId(2), ed.PinKind.input)
        imgui.bullet()
        imgui.same_line()
        imgui.text_unformatted("Switch")
        ed.end_pin()

        ed.begin_pin(ed.PinId(3), ed.PinKind.output)
        imgui.text_unformatted("Status")
        imgui.same_line()
        imgui.bullet()
        ed.end_pin()

        ed.end_node()

        ed.end()


def main() -> None:
    app = KnxGuiApp()

    runner_params = hello_imgui.RunnerParams()
    runner_params.app_window_params.window_title = "KNX ETS Node Editor"
    runner_params.app_window_params.window_geometry.size = (1280, 720)

    runner_params.callbacks.post_init = app.setup
    runner_params.callbacks.before_exit = app.shutdown
    runner_params.callbacks.show_gui = app.render

    hello_imgui.run(runner_params)


if __name__ == "__main__":
    main()
