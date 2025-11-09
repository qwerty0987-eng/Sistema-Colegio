import ttkbootstrap as ttkb

def aplicar_tema(root):
    ttkb.Style("darkly")
    root.configure(bg="#1F274D")
    root.option_add("*Font", ("Segoe UI", 10))
    return root