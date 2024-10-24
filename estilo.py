import tkinter as tk

def aplicar_estilo_botao(botao):
    """Aplica estilo ao botão."""
    botao.config(
        bg="#4CAF50",          # Cor de fundo
        fg="white",            # Cor do texto
        font=("Arial", 12, "bold"),  # Fonte e tamanho
        padx=10,              # Espaçamento horizontal
        pady=5,               # Espaçamento vertical
        borderwidth=2,        # Largura da borda
        relief="raised"       # Estilo da borda
    )

def aplicar_estilo_entry(entry):
    """Aplica estilo ao campo de entrada."""
    entry.config(
        bg="#f0f0f0",         # Cor de fundo
        fg="black",           # Cor do texto
        font=("Arial", 12),   # Fonte e tamanho
        borderwidth=1,        # Largura da borda
        relief="flat"         # Estilo da borda
    )

def aplicar_estilo_label(label):
    """Aplica estilo ao rótulo."""
    label.config(
        bg="white",           # Cor de fundo
        fg="black",           # Cor do texto
        font=("Arial", 14),   # Fonte e tamanho
    )

# Exemplo de como usar as funções no seu aplicativo
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Estilo do Aplicativo")

    # Criação de um botão
    botao = tk.Button(root, text="Clique aqui")
    aplicar_estilo_botao(botao)
    botao.pack(pady=10)

    # Criação de um campo de entrada
    entry = tk.Entry(root)
    aplicar_estilo_entry(entry)
    entry.pack(pady=10)

    # Criação de um rótulo
    label = tk.Label(root, text="Bem-vindo ao DataPolisher!")
    aplicar_estilo_label(label)
    label.pack(pady=10)

    root.mainloop()
