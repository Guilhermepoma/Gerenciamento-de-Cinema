import mysql.connector
from mysql.connector import Error
import customtkinter as ctk
from tkinter import messagebox, ttk, filedialog

ctk.set_default_color_theme("blue")

# =================== CONEXÃO COM BANCO =================== #
def conectar():
    try:
        connection = mysql.connector.connect(
            host="127.0.0.1",
            port="3306",
            user="root",
            password="",
            database="cinema"
        )
        return connection
    except Error as e:
        messagebox.showerror("Erro", f"Erro ao conectar ao banco: {e}")
        return None

# =================== LOGIN =================== #
def validate_login():
    cpf_user = cpf_entry.get()
    senha_user = senha_entry.get()

    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("SELECT * FROM cadastro_cliente WHERE cpf=%s AND senha=%s",
                   (cpf_user, senha_user))
    resultado = cursor.fetchone()

    cursor.close()
    conexao.close()

    if resultado:
        # ADMIN
        if cpf_user == "00000000000" and senha_user == "admin":
            messagebox.showinfo("Admin", "Bem-vindo, Administrador!")
            login_window.destroy()
            abrir_admin()
        # CLIENTE NORMAL
        else:
            messagebox.showinfo("Sucesso", "Bem-vindo!")
            login_window.destroy()
            abrir_sistema()
    else:
        messagebox.showerror("Erro", "CPF ou senha inválidos!")

# =================== REGISTRAR CLIENTE =================== #
def abrir_registro():
    reg_window = ctk.CTk()
    reg_window.geometry("400x430")
    reg_window.title("Registrar Cliente")

    font_reg = ctk.CTkFont(size=14)

    ctk.CTkLabel(reg_window, text="Nome:*", font=font_reg).pack()
    nome = ctk.CTkEntry(reg_window, width=250)
    nome.pack(pady=5)

    ctk.CTkLabel(reg_window, text="CPF:* (11 dígitos)", font=font_reg).pack()
    cpf = ctk.CTkEntry(reg_window, width=250)
    cpf.pack(pady=5)

    ctk.CTkLabel(reg_window, text="Senha:*", font=font_reg).pack()
    senha = ctk.CTkEntry(reg_window, show="*", width=250)
    senha.pack(pady=5)

    ctk.CTkLabel(reg_window, text="Email:*", font=font_reg).pack()
    email = ctk.CTkEntry(reg_window, width=250)
    email.pack(pady=5)

    ctk.CTkLabel(reg_window, text="Telefone:", font=font_reg).pack()
    telefone = ctk.CTkEntry(reg_window, width=250)
    telefone.pack(pady=5)

    def salvar_registro():
        nome_v = nome.get()
        cpf_v = cpf.get()
        senha_v = senha.get()
        email_v = email.get()
        telefone_v = telefone.get()

        if nome_v == "" or cpf_v == "" or senha_v == "" or email_v == "":
            messagebox.showwarning("Atenção", "Preencha todos os campos obrigatórios!")
            return

        conexao = conectar()
        cursor = conexao.cursor()

        try:
            cursor.execute("""
                INSERT INTO cadastro_cliente (nome, cpf, senha, email, telefone)
                VALUES (%s, %s, %s, %s, %s)
            """, (nome_v, cpf_v, senha_v, email_v, telefone_v))
            conexao.commit()
            messagebox.showinfo("Sucesso", "Cliente registrado com sucesso!")
            reg_window.destroy()
        except Error as e:
            messagebox.showerror("Erro", f"Erro ao salvar: {e}")
        finally:
            cursor.close()
            conexao.close()

    ctk.CTkButton(reg_window, text="Registrar", command=salvar_registro).pack(pady=20)
    reg_window.mainloop()

# =================== PAINEL DO CLIENTE =================== #
def abrir_sistema():
    app = ctk.CTk()
    app.geometry("650x300")
    app.title("Cinema - Cliente")

    title = ctk.CTkLabel(app, text="Sistema do Cliente",
                         font=ctk.CTkFont(size=20, weight="bold"))
    title.pack(pady=10)

    ctk.CTkButton(app, text="Comprar Ingresso").pack(pady=10)
    ctk.CTkButton(app, text="Sessões Disponíveis").pack(pady=10)
    ctk.CTkButton(app, text="Sair", command=app.destroy).pack(pady=20)

    app.mainloop()

# =================== PAINEL DO ADMIN =================== #
def abrir_admin():
    adm = ctk.CTk()
    adm.geometry("650x300")
    adm.title("Painel Administrativo")

    ctk.CTkLabel(adm, text="PAINEL ADMINISTRATIVO",
                 font=ctk.CTkFont(size=22, weight="bold")).pack(pady=20)

    ctk.CTkButton(adm, text="Gestão de Clientes", command=abrir_gestao_clientes).pack(pady=10)
    ctk.CTkButton(adm, text="Gestão de Filmes", command=abrir_gestao_filmes).pack(pady=10)
    ctk.CTkButton(adm, text="Gestão de Sessões").pack(pady=10)
    ctk.CTkButton(adm, text="Sair", command=adm.destroy).pack(pady=20)

    adm.mainloop()

# =================== GESTÃO DE CLIENTES =================== #
def abrir_gestao_clientes():
    cliente = ctk.CTk()
    cliente.geometry("800x500")
    cliente.title("Gestão de Clientes")

    ctk.CTkLabel(cliente, text="Clientes Cadastrados",
                 font=ctk.CTkFont(size=20, weight="bold")).pack(pady=10)

    frame = ttk.Frame(cliente)
    frame.pack(fill="both", expand=True, padx=10, pady=10)

    colunas = ("ID", "Nome", "CPF", "Email", "Telefone")
    tabela = ttk.Treeview(frame, columns=colunas, show="headings", height=15)

    for col in colunas:
        tabela.heading(col, text=col)
        tabela.column(col, width=150)

    tabela.pack(side="left", fill="both", expand=True)

    scroll = ttk.Scrollbar(frame, orient="vertical", command=tabela.yview)
    tabela.configure(yscrollcommand=scroll.set)
    scroll.pack(side="right", fill="y")

    def carregar_clientes():
        for item in tabela.get_children():
            tabela.delete(item)
        conexao = conectar()
        cursor = conexao.cursor()
        cursor.execute("SELECT id_cliente, nome, cpf, email, telefone FROM cadastro_cliente")
        dados = cursor.fetchall()
        for cli in dados:
            tabela.insert("", "end", values=cli)
        cursor.close()
        conexao.close()

    carregar_clientes()

    def excluir_cliente():
        item = tabela.selection()
        if not item:
            messagebox.showwarning("Atenção", "Selecione um cliente!")
            return
        cliente_sel = tabela.item(item)["values"]
        id_cliente = cliente_sel[0]
        if id_cliente == 1:
            messagebox.showwarning("Erro", "Não é possível excluir o administrador!")
            return
        conexao = conectar()
        cursor = conexao.cursor()
        cursor.execute("DELETE FROM cadastro_cliente WHERE id_cliente=%s", (id_cliente,))
        conexao.commit()
        cursor.close()
        conexao.close()
        carregar_clientes()
        messagebox.showinfo("Sucesso", "Cliente excluído!")

    ctk.CTkButton(cliente, text="Excluir Cliente Selecionado", command=excluir_cliente).pack(pady=5)

    cliente.mainloop()

# =================== GESTÃO DE FILMES =================== #
def abrir_gestao_filmes():
    filmes = ctk.CTk()
    filmes.geometry("900x600")
    filmes.title("Gestão de Filmes")

    ctk.CTkLabel(filmes, text="Filmes Cadastrados",
                 font=ctk.CTkFont(size=20, weight="bold")).pack(pady=10)

    frame = ttk.Frame(filmes)
    frame.pack(fill="both", expand=True, padx=10, pady=10)

    colunas = ("ID", "Título", "Gênero", "Duração", "Descrição", "Imagem")
    tabela = ttk.Treeview(frame, columns=colunas, show="headings", height=15)

    for col in colunas:
        tabela.heading(col, text=col)
        tabela.column(col, width=130)

    tabela.pack(side="left", fill="both", expand=True)

    scroll = ttk.Scrollbar(frame, orient="vertical", command=tabela.yview)
    tabela.configure(yscrollcommand=scroll.set)
    scroll.pack(side="right", fill="y")

    def carregar_filmes():
        for item in tabela.get_children():
            tabela.delete(item)
        conexao = conectar()
        cursor = conexao.cursor()
        cursor.execute("SELECT id_filme, titulo, genero, duracao, descricao, imagem FROM cadastro_filme")
        dados = cursor.fetchall()
        for f in dados:
            tabela.insert("", "end", values=f)
        cursor.close()
        conexao.close()

    carregar_filmes()

    # =================== ADICIONAR FILME =================== #
    def adicionar_filme():
        add_win = ctk.CTkToplevel(filmes)
        add_win.geometry("400x500")
        add_win.title("Adicionar Filme")

        ctk.CTkLabel(add_win, text="Título:*").pack(pady=5)
        titulo = ctk.CTkEntry(add_win, width=250)
        titulo.pack(pady=5)

        ctk.CTkLabel(add_win, text="Gênero:*").pack(pady=5)
        genero = ctk.CTkEntry(add_win, width=250)
        genero.pack(pady=5)

        ctk.CTkLabel(add_win, text="Duração (min):*").pack(pady=5)
        duracao = ctk.CTkEntry(add_win, width=250)
        duracao.pack(pady=5)

        ctk.CTkLabel(add_win, text="Descrição:*").pack(pady=5)
        descricao = ctk.CTkEntry(add_win, width=250)
        descricao.pack(pady=5)

        ctk.CTkLabel(add_win, text="Imagem:").pack(pady=5)
        caminho_imagem = ctk.StringVar()
        ctk.CTkEntry(add_win, textvariable=caminho_imagem, width=250).pack(pady=5)

        def escolher_imagem():
            caminho = filedialog.askopenfilename(
                filetypes=[("Arquivos de Imagem", "*.jpg *.png *.jpeg *.gif")]
            )
            if caminho:
                caminho_imagem.set(caminho)

        ctk.CTkButton(add_win, text="Selecionar Imagem", command=escolher_imagem).pack(pady=5)

        def salvar_filme():
            t = titulo.get()
            g = genero.get()
            d = duracao.get()
            desc = descricao.get()
            img = caminho_imagem.get()
            if t == "" or g == "" or d == "" or desc == "":
                messagebox.showwarning("Atenção", "Preencha todos os campos obrigatórios!")
                return
            conexao = conectar()
            cursor = conexao.cursor()
            try:
                cursor.execute("""
                    INSERT INTO cadastro_filme (titulo, genero, duracao, descricao, imagem)
                    VALUES (%s, %s, %s, %s, %s)
                """, (t, g, d, desc, img))
                conexao.commit()
                messagebox.showinfo("Sucesso", "Filme adicionado!")
                add_win.destroy()
                carregar_filmes()
            except Error as e:
                messagebox.showerror("Erro", f"Erro ao adicionar filme: {e}")
            finally:
                cursor.close()
                conexao.close()

        ctk.CTkButton(add_win, text="Salvar Filme", command=salvar_filme).pack(pady=20)

    # =================== EXCLUIR FILME =================== #
    def excluir_filme():
        item = tabela.selection()
        if not item:
            messagebox.showwarning("Atenção", "Selecione um filme!")
            return
        filme_sel = tabela.item(item)["values"]
        id_filme = filme_sel[0]
        conexao = conectar()
        cursor = conexao.cursor()
        cursor.execute("DELETE FROM cadastro_filme WHERE id_filme=%s", (id_filme,))
        conexao.commit()
        cursor.close()
        conexao.close()
        carregar_filmes()
        messagebox.showinfo("Sucesso", "Filme excluído!")

    ctk.CTkButton(filmes, text="Atualizar", command=carregar_filmes).pack(pady=10)
    ctk.CTkButton(filmes, text="Adicionar Filme", command=adicionar_filme).pack(pady=5)
    ctk.CTkButton(filmes, text="Excluir Filme Selecionado", command=excluir_filme).pack(pady=5)

    filmes.mainloop()

# =================== TELA LOGIN =================== #
login_window = ctk.CTk()
login_window.geometry("400x300")
login_window.title("Login - Cinema")

ctk.CTkLabel(login_window, text="CPF:", font=ctk.CTkFont(size=14)).pack(pady=5)
cpf_entry = ctk.CTkEntry(login_window, width=200)
cpf_entry.pack()

ctk.CTkLabel(login_window, text="Senha:", font=ctk.CTkFont(size=14)).pack(pady=5)
senha_entry = ctk.CTkEntry(login_window, show="*", width=200)
senha_entry.pack(pady=5)

ctk.CTkButton(login_window, text="Login", command=validate_login).pack(pady=10)
ctk.CTkButton(login_window, text="Registrar Novo Cliente", command=abrir_registro).pack(pady=5)

login_window.mainloop()