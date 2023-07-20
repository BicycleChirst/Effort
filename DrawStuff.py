import glfw
import OpenGL.GL as GL

import imgui
from imgui.integrations.glfw import GlfwRenderer

def CreateWindow():
    # initialize the glfw library
    if not glfw.init():
        return

# not necessary
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL.GL_TRUE)

    # Create a windowed-mode window and it's OpenGL context
    epic_glfw_window = glfw.create_window(640, 480, "Epic GLFW window", None, None)
    glfw.make_context_current(epic_glfw_window)
    glfw.swap_interval(1)  # vsync

    if not epic_glfw_window:
        glfw.terminate()
        return

    imgui.create_context()
    imgui.get_io().display_size = 100, 100
    imgui.get_io().fonts.get_tex_data_as_rgba32()
    impl = GlfwRenderer(epic_glfw_window)

    # Loop until the window is closed
    while not glfw.window_should_close(epic_glfw_window):
        glfw.poll_events()
        impl.process_inputs()
        render_frame()
        impl.render(imgui.get_draw_data())
        glfw.swap_buffers(epic_glfw_window)

    impl.shutdown()
    glfw.terminate()


def render_frame():
    imgui.new_frame()

    # opens new window context
    imgui.begin("Epic window!", True)
    # draws the text label inside the window
    imgui.text("Epic text!")
    # closes window context
    imgui.end()

    # built-in test window
    imgui.show_test_window()

# very necessary
    GL.glClearColor(0.1, 0.1, 0.1, 0.1)
    GL.glClear(GL.GL_COLOR_BUFFER_BIT)

    # pass all drawing commands to the rendering pipeline
    # and close the frame context
    imgui.render()
    #imgui.end_frame() # .render already calls this


if __name__ == "__main__":
    CreateWindow()