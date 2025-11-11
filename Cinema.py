import mysql.connector
from mysql.connector import Error
import customtkinter as ctk
from tkinter import messagebox, ttk, filedialog
from datetime import datetime

ctk.set_default_color_theme("blue")

# Variável global para armazenar o ID do cliente logado
ID_CLIENTE_LOGADO = None

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
    global ID_CLIENTE_LOGADO
    cpf_user = cpf_entry.get()
    senha_user = senha_entry.get()

    conexao = conectar()
    if not conexao:
        return

    cursor = conexao.cursor()
    cursor.execute("SELECT id_cliente, nome FROM cadastro_cliente WHERE cpf=%s AND senha=%s",
                   (cpf_user, senha_user))
    resultado = cursor.fetchone()

    cursor.close()
    conexao.close()

    if resultado:
        ID_CLIENTE_LOGADO = resultado[0]
        nome_cliente = resultado[1]
        # ADMIN
        if cpf_user == "00000000000" and senha_user == "admin":
            messagebox.showinfo("Admin", f"Bem-vindo, Administrador! ({nome_cliente})")
            login_window.destroy()
            abrir_admin()
        # CLIENTE NORMAL
        else:
            messagebox.showinfo("Sucesso", f"Bem-vindo, {nome_cliente}!")
            login_window.destroy()
            abrir_sistema()
    else:
        messagebox.showerror("Erro", "CPF ou senha inválidos!")

# =================== REGISTRAR CLIENTE =================== #
def abrir_registro():
    reg_window = ctk.CTkToplevel(login_window)
    reg_window.geometry("400x430")
    reg_window.title("Registrar Cliente")
    reg_window.grab_set() # Bloqueia a janela principal

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
        
        if len(cpf_v) != 11 or not cpf_v.isdigit():
            messagebox.showwarning("Atenção", "O CPF deve conter 11 dígitos numéricos.")
            return

        conexao = conectar()
        if not conexao:
            return
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
            if 'Duplicate entry' in str(e) and 'cpf' in str(e):
                messagebox.showerror("Erro", "CPF já cadastrado.")
            elif 'Duplicate entry' in str(e) and 'email' in str(e):
                messagebox.showerror("Erro", "Email já cadastrado.")
            else:
                messagebox.showerror("Erro", f"Erro ao salvar: {e}")
        finally:
            cursor.close()
            conexao.close()

    ctk.CTkButton(reg_window, text="Registrar", command=salvar_registro).pack(pady=20)
    reg_window.mainloop()

# =================== PAINEL DO CLIENTE =================== #
def abrir_sistema():
    app = ctk.CTk()
    app.geometry("400x400")
    app.title("Cinema - Cliente")

    title = ctk.CTkLabel(app, text="Sistema do Cliente",
                         font=ctk.CTkFont(size=20, weight="bold"))
    title.pack(pady=20)

    frame_botoes = ctk.CTkFrame(app)
    frame_botoes.pack(pady=10, padx=20, fill="x")

    ctk.CTkButton(frame_botoes, text="Ver Sessões e Comprar Ingresso", command=lambda: abrir_compra_ingresso(app)).pack(pady=10, padx=10)
    ctk.CTkButton(frame_botoes, text="Comprar Produtos (Concessão)", command=lambda: abrir_compra_produtos(app)).pack(pady=10, padx=10)
    ctk.CTkButton(frame_botoes, text="Ver Histórico de Compras", command=lambda: abrir_historico_compras(app)).pack(pady=10, padx=10)
    ctk.CTkButton(app, text="Sair", command=app.destroy).pack(pady=20)

    app.mainloop()

# ========== COMPRA DE INGRESSO ========== #
def abrir_compra_ingresso(parent_window):
    compra_win = ctk.CTkToplevel(parent_window)
    compra_win.geometry("900x600")
    compra_win.title("Sessões e Compra de Ingresso")
    compra_win.grab_set()

    ctk.CTkLabel(compra_win, text="Sessões Disponíveis",
                 font=ctk.CTkFont(size=20, weight="bold")).pack(pady=10)

    frame = ttk.Frame(compra_win)
    frame.pack(fill="both", expand=True, padx=10, pady=10)

    colunas = ("ID Sessão", "Filme", "Sala", "Horário", "Preço (R$)", "Duração")
    tabela = ttk.Treeview(frame, columns=colunas, show="headings", height=15)

    for col in colunas:
        tabela.heading(col, text=col)
        tabela.column(col, width=120)

    tabela.pack(side="left", fill="both", expand=True)

    scroll = ttk.Scrollbar(frame, orient="vertical", command=tabela.yview)
    tabela.configure(yscrollcommand=scroll.set)
    scroll.pack(side="right", fill="y")

    def carregar_sessoes_cliente():
        for item in tabela.get_children():
            tabela.delete(item)
        conexao = conectar()
        if not conexao: return
        cursor = conexao.cursor()
        cursor.execute("""
            SELECT s.id_sessao, f.titulo, s.sala, s.horario, s.preco, f.duracao
            FROM sessoes s
            INNER JOIN cadastro_filme f ON s.id_filme = f.id_filme
            WHERE s.horario > NOW()
            ORDER BY s.horario
        """)
        dados = cursor.fetchall()
        for s in dados:
            # Formata o horário e o preço para exibição
            horario_formatado = s[3].strftime("%d/%m/%Y %H:%M")
            preco_formatado = f"{s[4]:.2f}".replace('.', ',') # Formata para R$ X,XX
            tabela.insert("", "end", values=(s[0], s[1], s[2], horario_formatado, preco_formatado, s[5]))
        cursor.close()
        conexao.close()

    carregar_sessoes_cliente()

    # Frame para a compra
    frame_compra = ctk.CTkFrame(compra_win)
    frame_compra.pack(pady=10, padx=10, fill="x")

    ctk.CTkLabel(frame_compra, text="Quantidade de Ingressos:").pack(side="left", padx=5)
    qtd_ingresso = ctk.CTkEntry(frame_compra, width=50)
    qtd_ingresso.insert(0, "1")
    qtd_ingresso.pack(side="left", padx=5)

    def comprar_ingresso():
        item = tabela.selection()
        if not item:
            messagebox.showwarning("Atenção", "Selecione uma sessão!")
            return

        try:
            quantidade = int(qtd_ingresso.get())
            if quantidade <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Atenção", "Quantidade inválida!")
            return

        sessao_sel = tabela.item(item)["values"]
        id_sessao = sessao_sel[0]
        preco_unitario_str = sessao_sel[4].replace(',', '.') # Converte de volta para float
        preco_unitario = float(preco_unitario_str)
        filme_titulo = sessao_sel[1]
        horario = sessao_sel[3]

        total = quantidade * preco_unitario
        total_formatado = f"{total:.2f}".replace('.', ',')

        confirmar = messagebox.askyesno("Confirmação de Compra",
                                        f"Deseja comprar {quantidade} ingresso(s) para:\n"
                                        f"Filme: {filme_titulo}\n"
                                        f"Horário: {horario}\n"
                                        f"Total: R$ {total_formatado}?")

        if confirmar:
            conexao = conectar()
            if not conexao: return
            cursor = conexao.cursor()
            try:
                cursor.execute("""
                    INSERT INTO ingressos_comprados (id_cliente, id_sessao, quantidade)
                    VALUES (%s, %s, %s)
                """, (ID_CLIENTE_LOGADO, id_sessao, quantidade))
                conexao.commit()
                messagebox.showinfo("Sucesso", "Ingresso(s) comprado(s) com sucesso!")
            except Error as e:
                messagebox.showerror("Erro", f"Erro ao comprar ingresso: {e}")
            finally:
                cursor.close()
                conexao.close()

    ctk.CTkButton(frame_compra, text="Comprar Ingresso Selecionado", command=comprar_ingresso).pack(side="left", padx=10)
    ctk.CTkButton(compra_win, text="Fechar", command=compra_win.destroy).pack(pady=10)

# ========== COMPRA DE PRODUTOS ========== #
def abrir_compra_produtos(parent_window):
    produtos_win = ctk.CTkToplevel(parent_window)
    produtos_win.geometry("700x500")
    produtos_win.title("Compra de Produtos (Concessão)")
    produtos_win.grab_set()

    ctk.CTkLabel(produtos_win, text="Produtos Disponíveis",
                 font=ctk.CTkFont(size=20, weight="bold")).pack(pady=10)

    frame = ttk.Frame(produtos_win)
    frame.pack(fill="both", expand=True, padx=10, pady=10)

    colunas = ("ID", "Nome", "Descrição", "Preço (R$)", "Estoque")
    tabela = ttk.Treeview(frame, columns=colunas, show="headings", height=15)

    for col in colunas:
        tabela.heading(col, text=col)
        tabela.column(col, width=120)

    tabela.pack(side="left", fill="both", expand=True)

    scroll = ttk.Scrollbar(frame, orient="vertical", command=tabela.yview)
    tabela.configure(yscrollcommand=scroll.set)
    scroll.pack(side="right", fill="y")

    def carregar_produtos_cliente():
        for item in tabela.get_children():
            tabela.delete(item)
        conexao = conectar()
        if not conexao: return
        cursor = conexao.cursor()
        cursor.execute("SELECT id_produto, nome, descricao, preco, estoque FROM produtos WHERE estoque > 0")
        dados = cursor.fetchall()
        for p in dados:
            tabela.insert("", "end", values=p)
        cursor.close()
        conexao.close()

    carregar_produtos_cliente()

    # Frame para a compra
    frame_compra = ctk.CTkFrame(produtos_win)
    frame_compra.pack(pady=10, padx=10, fill="x")

    ctk.CTkLabel(frame_compra, text="Quantidade:").pack(side="left", padx=5)
    qtd_produto = ctk.CTkEntry(frame_compra, width=50)
    qtd_produto.insert(0, "1")
    qtd_produto.pack(side="left", padx=5)

    def comprar_produto():
        item = tabela.selection()
        if not item:
            messagebox.showwarning("Atenção", "Selecione um produto!")
            return

        try:
            quantidade = int(qtd_produto.get())
            if quantidade <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Atenção", "Quantidade inválida!")
            return

        produto_sel = tabela.item(item)["values"]
        id_produto = produto_sel[0]
        nome_produto = produto_sel[1]
        preco_unitario = float(produto_sel[3])
        estoque_atual = produto_sel[4]

        if quantidade > estoque_atual:
            messagebox.showwarning("Atenção", f"Estoque insuficiente. Disponível: {estoque_atual}")
            return

        confirmar = messagebox.askyesno("Confirmação de Compra",
                                        f"Deseja comprar {quantidade} unidade(s) de:\n"
                                        f"Produto: {nome_produto}\n"
                                        f"Total: R$ {quantidade * preco_unitario:.2f}?")

        if confirmar:
            conexao = conectar()
            if not conexao: return
            cursor = conexao.cursor()
            try:
                # 1. Inserir na tabela de compras_produtos
                cursor.execute("""
                    INSERT INTO compras_produtos (id_cliente, id_produto, quantidade, preco_unitario)
                    VALUES (%s, %s, %s, %s)
                """, (ID_CLIENTE_LOGADO, id_produto, quantidade, preco_unitario))

                # 2. Atualizar o estoque
                cursor.execute("""
                    UPDATE produtos SET estoque = estoque - %s WHERE id_produto = %s
                """, (quantidade, id_produto))

                conexao.commit()
                messagebox.showinfo("Sucesso", "Produto(s) comprado(s) com sucesso!")
                carregar_produtos_cliente() # Recarrega a lista para atualizar o estoque
            except Error as e:
                messagebox.showerror("Erro", f"Erro ao comprar produto: {e}")
            finally:
                cursor.close()
                conexao.close()

    ctk.CTkButton(frame_compra, text="Comprar Produto Selecionado", command=comprar_produto).pack(side="left", padx=10)
    ctk.CTkButton(produtos_win, text="Fechar", command=produtos_win.destroy).pack(pady=10)

# ========== HISTÓRICO DE COMPRAS ========== #
def abrir_historico_compras(parent_window):
    historico_win = ctk.CTkToplevel(parent_window)
    historico_win.geometry("1000x600")
    historico_win.title("Histórico de Compras")
    historico_win.grab_set()

    ctk.CTkLabel(historico_win, text="Histórico de Ingressos",
                 font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)

    # Frame para Ingressos
    frame_ingressos = ctk.CTkFrame(historico_win)
    frame_ingressos.pack(fill="x", padx=10, pady=5)

    colunas_ing = ("ID Compra", "Filme", "Sala", "Horário", "Quantidade", "Data Compra")
    tabela_ingressos = ttk.Treeview(frame_ingressos, columns=colunas_ing, show="headings", height=8)

    for col in colunas_ing:
        tabela_ingressos.heading(col, text=col)
        tabela_ingressos.column(col, width=150)

    tabela_ingressos.pack(side="left", fill="both", expand=True)
    scroll_ing = ttk.Scrollbar(frame_ingressos, orient="vertical", command=tabela_ingressos.yview)
    tabela_ingressos.configure(yscrollcommand=scroll_ing.set)
    scroll_ing.pack(side="right", fill="y")

    def carregar_historico_ingressos():
        for item in tabela_ingressos.get_children():
            tabela_ingressos.delete(item)
        conexao = conectar()
        if not conexao: return
        cursor = conexao.cursor()
        cursor.execute("""
            SELECT ic.id_compra, f.titulo, s.sala, s.horario, ic.quantidade, ic.data_compra
            FROM ingressos_comprados ic
            INNER JOIN sessoes s ON ic.id_sessao = s.id_sessao
            INNER JOIN cadastro_filme f ON s.id_filme = f.id_filme
            WHERE ic.id_cliente = %s
            ORDER BY ic.data_compra DESC
        """, (ID_CLIENTE_LOGADO,))
        dados = cursor.fetchall()
        for i in dados:
            horario_formatado = i[3].strftime("%d/%m/%Y %H:%M")
            data_compra_formatada = i[5].strftime("%d/%m/%Y %H:%M")
            tabela_ingressos.insert("", "end", values=(i[0], i[1], i[2], horario_formatado, i[4], data_compra_formatada))
        cursor.close()
        conexao.close()

    carregar_historico_ingressos()

    ctk.CTkLabel(historico_win, text="Histórico de Produtos (Concessão)",
                 font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)

    # Frame para Produtos
    frame_produtos = ctk.CTkFrame(historico_win)
    frame_produtos.pack(fill="x", padx=10, pady=5)

    colunas_prod = ("ID Compra", "Produto", "Quantidade", "Preço Unitário (R$)", "Data Compra")
    tabela_produtos = ttk.Treeview(frame_produtos, columns=colunas_prod, show="headings", height=8)

    for col in colunas_prod:
        tabela_produtos.heading(col, text=col)
        tabela_produtos.column(col, width=150)

    tabela_produtos.pack(side="left", fill="both", expand=True)
    scroll_prod = ttk.Scrollbar(frame_produtos, orient="vertical", command=tabela_produtos.yview)
    tabela_produtos.configure(yscrollcommand=scroll_prod.set)
    scroll_prod.pack(side="right", fill="y")

    def carregar_historico_produtos():
        for item in tabela_produtos.get_children():
            tabela_produtos.delete(item)
        conexao = conectar()
        if not conexao: return
        cursor = conexao.cursor()
        cursor.execute("""
            SELECT cp.id_compra_produto, p.nome, cp.quantidade, cp.preco_unitario, cp.data_compra
            FROM compras_produtos cp
            INNER JOIN produtos p ON cp.id_produto = p.id_produto
            WHERE cp.id_cliente = %s
            ORDER BY cp.data_compra DESC
        """, (ID_CLIENTE_LOGADO,))
        dados = cursor.fetchall()
        for p in dados:
            data_compra_formatada = p[4].strftime("%d/%m/%Y %H:%M")
            tabela_produtos.insert("", "end", values=(p[0], p[1], p[2], p[3], data_compra_formatada))
        cursor.close()
        conexao.close()

    carregar_historico_produtos()

    ctk.CTkButton(historico_win, text="Fechar", command=historico_win.destroy).pack(pady=10)

# =================== RELATÓRIOS DE VENDAS =================== #
def abrir_relatorios_vendas():
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

    relatorios = ctk.CTkToplevel()
    relatorios.geometry("600x500")
    relatorios.title("Relatórios de Vendas")
    relatorios.grab_set()

    ctk.CTkLabel(relatorios, text="RELATÓRIOS DE VENDAS",
                 font=ctk.CTkFont(size=22, weight="bold")).pack(pady=20)

    conexao = conectar()
    if not conexao:
        return
    cursor = conexao.cursor()

    # 1. Cálculo do Faturamento Total de Ingressos
    faturamento_ingressos = 0.0
    try:
        cursor.execute("""
            SELECT SUM(ic.quantidade * s.preco)
            FROM ingressos_comprados ic
            INNER JOIN sessoes s ON ic.id_sessao = s.id_sessao
        """)
        resultado = cursor.fetchone()
        if resultado and resultado[0] is not None:
            faturamento_ingressos = float(resultado[0])
    except Error as e:
        messagebox.showerror("Erro SQL", f"Erro ao calcular faturamento de ingressos: {e}")

    # 2. Cálculo do Faturamento Total de Produtos
    faturamento_produtos = 0.0
    try:
        cursor.execute("""
            SELECT SUM(quantidade * preco_unitario)
            FROM compras_produtos
        """)
        resultado = cursor.fetchone()
        if resultado and resultado[0] is not None:
            faturamento_produtos = float(resultado[0])
    except Error as e:
        messagebox.showerror("Erro SQL", f"Erro ao calcular faturamento de produtos: {e}")

    faturamento_total = faturamento_ingressos + faturamento_produtos

    cursor.close()
    conexao.close()

    # Exibição do Faturamento
    ctk.CTkLabel(relatorios, text="Faturamento Total",
                 font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)
    
    ctk.CTkLabel(relatorios, text=f"Ingressos: R$ {faturamento_ingressos:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
                 font=ctk.CTkFont(size=14)).pack()
    ctk.CTkLabel(relatorios, text=f"Produtos: R$ {faturamento_produtos:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
                 font=ctk.CTkFont(size=14)).pack()
    ctk.CTkLabel(relatorios, text=f"TOTAL GERAL: R$ {faturamento_total:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
                 font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)

    # Frame para Produtos Mais Vendidos
    frame_produtos_vendidos = ctk.CTkFrame(relatorios)
    frame_produtos_vendidos.pack(pady=20, padx=20, fill="both", expand=True)
    
    ctk.CTkLabel(frame_produtos_vendidos, text="Produtos Mais Vendidos (Top 5)",
                 font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)

    # 3. Produtos Mais Vendidos
    mais_vendidos = []
    conexao = conectar()
    if conexao:
        cursor = conexao.cursor()
        try:
            cursor.execute("""
                SELECT p.nome, SUM(cp.quantidade) AS total_vendido
                FROM compras_produtos cp
                INNER JOIN produtos p ON cp.id_produto = p.id_produto
                GROUP BY p.nome
                ORDER BY total_vendido DESC
                LIMIT 5
            """)
            mais_vendidos = cursor.fetchall()
            
            if mais_vendidos:
                for nome, quantidade in mais_vendidos:
                    ctk.CTkLabel(frame_produtos_vendidos, text=f"- {nome}: {quantidade} unidades vendidas",
                                 font=ctk.CTkFont(size=14)).pack(anchor="w", padx=20)
            else:
                ctk.CTkLabel(frame_produtos_vendidos, text="Nenhum produto vendido ainda.",
                             font=ctk.CTkFont(size=14)).pack(pady=10)

        except Error as e:
            messagebox.showerror("Erro SQL", f"Erro ao buscar produtos mais vendidos: {e}")
        finally:
            cursor.close()
            conexao.close()

    # 4. Gráfico dos Produtos Mais Vendidos (tema escuro)
    if mais_vendidos:
        nomes = [item[0] for item in mais_vendidos]
        quantidades = [item[1] for item in mais_vendidos]

        fig, ax = plt.subplots(figsize=(5, 3))
        ax.bar(nomes, quantidades, color='#1f77b4')

        # Estilo escuro
        ax.set_facecolor('#2b2b2b')
        fig.patch.set_facecolor('#2b2b2b')
        ax.tick_params(colors='white')
        ax.title.set_color('white')
        ax.xaxis.label.set_color('white')
        ax.yaxis.label.set_color('white')

        ax.set_title("Top 5 Produtos Mais Vendidos")
        ax.set_xlabel("Produto")
        ax.set_ylabel("Quantidade Vendida")
        plt.xticks(rotation=30, ha='right')

        canvas = FigureCanvasTkAgg(fig, master=frame_produtos_vendidos)
        canvas.draw()
        canvas.get_tk_widget().pack(pady=10)

    relatorios.mainloop()

# =================== PAINEL DO ADMIN =================== #
def abrir_admin():
    adm = ctk.CTk()
    adm.geometry("400x500")
    adm.title("Painel Administrativo")

    ctk.CTkLabel(adm, text="PAINEL ADMINISTRATIVO",
                 font=ctk.CTkFont(size=22, weight="bold")).pack(pady=20)

    frame_botoes = ctk.CTkFrame(adm)
    frame_botoes.pack(pady=10, padx=20, fill="x")

    ctk.CTkButton(frame_botoes, text="Gestão de Clientes", command=abrir_gestao_clientes).pack(pady=10, padx=10)
    ctk.CTkButton(frame_botoes, text="Gestão de Filmes", command=abrir_gestao_filmes).pack(pady=10, padx=10)
    ctk.CTkButton(frame_botoes, text="Gestão de Sessões", command=abrir_gestao_sessoes).pack(pady=10, padx=10)
    ctk.CTkButton(frame_botoes, text="Gestão de Produtos (Concessão)", command=abrir_gestao_produtos).pack(pady=10, padx=10)
    ctk.CTkButton(frame_botoes, text="Relatórios de Vendas", command=abrir_relatorios_vendas).pack(pady=10, padx=10)
    ctk.CTkButton(adm, text="Sair", command=adm.destroy).pack(pady=20)

    adm.mainloop()

# =================== GESTÃO DE CLIENTES =================== #
def abrir_gestao_clientes():
    cliente = ctk.CTkToplevel()
    cliente.geometry("800x500")
    cliente.title("Gestão de Clientes")
    cliente.grab_set()

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
        if not conexao: return
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
        nome_cliente = cliente_sel[1]

        if id_cliente == 1:
            messagebox.showwarning("Erro", "Não é possível excluir o administrador!")
            return
        
        confirmar = messagebox.askyesno("Confirmação de Exclusão",
                                        f"Tem certeza que deseja excluir o cliente {nome_cliente} (ID: {id_cliente})?\n"
                                        "Esta ação é irreversível e excluirá todos os dados relacionados (ingressos, compras de produtos).")
        
        if confirmar:
            conexao = conectar()
            if not conexao: return
            cursor = conexao.cursor()
            try:
                cursor.execute("DELETE FROM cadastro_cliente WHERE id_cliente=%s", (id_cliente,))
                conexao.commit()
                carregar_clientes()
                messagebox.showinfo("Sucesso", "Cliente excluído!")
            except Error as e:
                messagebox.showerror("Erro", f"Erro ao excluir: {e}")
            finally:
                cursor.close()
                conexao.close()

    def editar_cliente():
        item = tabela.selection()
        if not item:
            messagebox.showwarning("Atenção", "Selecione um cliente para editar!")
            return
        
        cliente_sel = tabela.item(item)["values"]
        id_cliente = cliente_sel[0]
        
        edit_win = ctk.CTkToplevel(cliente)
        edit_win.geometry("400x400")
        edit_win.title(f"Editar Cliente ID: {id_cliente}")
        edit_win.grab_set()

        ctk.CTkLabel(edit_win, text="Nome:").pack()
        nome = ctk.CTkEntry(edit_win, width=250)
        nome.insert(0, cliente_sel[1])
        nome.pack(pady=5)

        ctk.CTkLabel(edit_win, text="CPF:").pack()
        cpf = ctk.CTkEntry(edit_win, width=250)
        cpf.insert(0, cliente_sel[2])
        cpf.pack(pady=5)

        ctk.CTkLabel(edit_win, text="Email:").pack()
        email = ctk.CTkEntry(edit_win, width=250)
        email.insert(0, cliente_sel[3])
        email.pack(pady=5)

        ctk.CTkLabel(edit_win, text="Telefone:").pack()
        telefone = ctk.CTkEntry(edit_win, width=250)
        telefone.insert(0, cliente_sel[4] if cliente_sel[4] else "")
        telefone.pack(pady=5)

        # Não edita a senha por aqui, seria em outra tela de redefinição
        
        def salvar_edicao():
            nome_v = nome.get()
            cpf_v = cpf.get()
            email_v = email.get()
            telefone_v = telefone.get()

            if nome_v == "" or cpf_v == "" or email_v == "":
                messagebox.showwarning("Atenção", "Preencha todos os campos obrigatórios!")
                return
            
            conexao = conectar()
            if not conexao: return
            cursor = conexao.cursor()
            try:
                cursor.execute("""
                    UPDATE cadastro_cliente SET nome=%s, cpf=%s, email=%s, telefone=%s
                    WHERE id_cliente=%s
                """, (nome_v, cpf_v, email_v, telefone_v, id_cliente))
                conexao.commit()
                messagebox.showinfo("Sucesso", "Cliente atualizado com sucesso!")
                edit_win.destroy()
                carregar_clientes()
            except Error as e:
                if 'Duplicate entry' in str(e) and 'cpf' in str(e):
                    messagebox.showerror("Erro", "CPF já cadastrado para outro cliente.")
                elif 'Duplicate entry' in str(e) and 'email' in str(e):
                    messagebox.showerror("Erro", "Email já cadastrado para outro cliente.")
                else:
                    messagebox.showerror("Erro", f"Erro ao atualizar: {e}")
            finally:
                cursor.close()
                conexao.close()

        ctk.CTkButton(edit_win, text="Salvar Alterações", command=salvar_edicao).pack(pady=20)

    frame_botoes = ctk.CTkFrame(cliente)
    frame_botoes.pack(pady=10)
    ctk.CTkButton(frame_botoes, text="Atualizar Lista", command=carregar_clientes).pack(side="left", padx=5)
    ctk.CTkButton(frame_botoes, text="Editar Cliente Selecionado", command=editar_cliente).pack(side="left", padx=5)
    ctk.CTkButton(frame_botoes, text="Excluir Cliente Selecionado", command=excluir_cliente).pack(side="left", padx=5)

# =================== GESTÃO DE FILMES =================== #
def abrir_gestao_filmes():
    filmes = ctk.CTkToplevel()
    filmes.geometry("900x600")
    filmes.title("Gestão de Filmes")
    filmes.grab_set()

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
        if not conexao: return
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
        add_win.grab_set()

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

        ctk.CTkLabel(add_win, text="Caminho Imagem:").pack(pady=5)
        caminho_imagem = ctk.StringVar()
        entry_imagem = ctk.CTkEntry(add_win, textvariable=caminho_imagem, width=250)
        entry_imagem.pack(pady=5)

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
            
            try:
                int(d)
            except ValueError:
                messagebox.showwarning("Atenção", "Duração deve ser um número inteiro.")
                return

            conexao = conectar()
            if not conexao: return
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
        titulo_filme = filme_sel[1]

        confirmar = messagebox.askyesno("Confirmação de Exclusão",
                                        f"Tem certeza que deseja excluir o filme '{titulo_filme}' (ID: {id_filme})?\n"
                                        "Esta ação é irreversível e excluirá todas as sessões e ingressos relacionados.")
        
        if confirmar:
            conexao = conectar()
            if not conexao: return
            cursor = conexao.cursor()
            try:
                cursor.execute("DELETE FROM cadastro_filme WHERE id_filme=%s", (id_filme,))
                conexao.commit()
                carregar_filmes()
                messagebox.showinfo("Sucesso", "Filme excluído!")
            except Error as e:
                messagebox.showerror("Erro", f"Erro ao excluir: {e}")
            finally:
                cursor.close()
                conexao.close()

    # =================== EDITAR FILME =================== #
    def editar_filme():
        item = tabela.selection()
        if not item:
            messagebox.showwarning("Atenção", "Selecione um filme para editar!")
            return
        
        filme_sel = tabela.item(item)["values"]
        id_filme = filme_sel[0]
        
        edit_win = ctk.CTkToplevel(filmes)
        edit_win.geometry("400x550")
        edit_win.title(f"Editar Filme ID: {id_filme}")
        edit_win.grab_set()

        ctk.CTkLabel(edit_win, text="Título:").pack(pady=5)
        titulo = ctk.CTkEntry(edit_win, width=250)
        titulo.insert(0, filme_sel[1])
        titulo.pack(pady=5)

        ctk.CTkLabel(edit_win, text="Gênero:").pack(pady=5)
        genero = ctk.CTkEntry(edit_win, width=250)
        genero.insert(0, filme_sel[2])
        genero.pack(pady=5)

        ctk.CTkLabel(edit_win, text="Duração (min):").pack(pady=5)
        duracao = ctk.CTkEntry(edit_win, width=250)
        duracao.insert(0, filme_sel[3])
        duracao.pack(pady=5)

        ctk.CTkLabel(edit_win, text="Descrição:").pack(pady=5)
        descricao = ctk.CTkEntry(edit_win, width=250)
        descricao.insert(0, filme_sel[4])
        descricao.pack(pady=5)

        ctk.CTkLabel(edit_win, text="Caminho Imagem:").pack(pady=5)
        caminho_imagem = ctk.StringVar(value=filme_sel[5] if filme_sel[5] else "")
        entry_imagem = ctk.CTkEntry(edit_win, textvariable=caminho_imagem, width=250)
        entry_imagem.pack(pady=5)

        def escolher_imagem():
            caminho = filedialog.askopenfilename(
                filetypes=[("Arquivos de Imagem", "*.jpg *.png *.jpeg *.gif")]
            )
            if caminho:
                caminho_imagem.set(caminho)

        ctk.CTkButton(edit_win, text="Selecionar Imagem", command=escolher_imagem).pack(pady=5)

        def salvar_edicao():
            t = titulo.get()
            g = genero.get()
            d = duracao.get()
            desc = descricao.get()
            img = caminho_imagem.get()

            if t == "" or g == "" or d == "" or desc == "":
                messagebox.showwarning("Atenção", "Preencha todos os campos obrigatórios!")
                return
            
            try:
                int(d)
            except ValueError:
                messagebox.showwarning("Atenção", "Duração deve ser um número inteiro.")
                return

            conexao = conectar()
            if not conexao: return
            cursor = conexao.cursor()
            try:
                cursor.execute("""
                    UPDATE cadastro_filme SET titulo=%s, genero=%s, duracao=%s, descricao=%s, imagem=%s
                    WHERE id_filme=%s
                """, (t, g, d, desc, img, id_filme))
                conexao.commit()
                messagebox.showinfo("Sucesso", "Filme atualizado com sucesso!")
                edit_win.destroy()
                carregar_filmes()
            except Error as e:
                messagebox.showerror("Erro", f"Erro ao atualizar filme: {e}")
            finally:
                cursor.close()
                conexao.close()

        ctk.CTkButton(edit_win, text="Salvar Alterações", command=salvar_edicao).pack(pady=20)

    frame_botoes = ctk.CTkFrame(filmes)
    frame_botoes.pack(pady=10)
    ctk.CTkButton(frame_botoes, text="Atualizar Lista", command=carregar_filmes).pack(side="left", padx=5)
    ctk.CTkButton(frame_botoes, text="Adicionar Filme", command=adicionar_filme).pack(side="left", padx=5)
    ctk.CTkButton(frame_botoes, text="Editar Filme Selecionado", command=editar_filme).pack(side="left", padx=5)
    ctk.CTkButton(frame_botoes, text="Excluir Filme Selecionado", command=excluir_filme).pack(side="left", padx=5)

# =================== GESTÃO DE SESSÕES =================== #
def abrir_gestao_sessoes():
    sessao = ctk.CTkToplevel()
    sessao.geometry("900x600")
    sessao.title("Gestão de Sessões")
    sessao.grab_set()

    ctk.CTkLabel(sessao, text="Sessões Cadastradas",
                 font=ctk.CTkFont(size=20, weight="bold")).pack(pady=10)

    frame = ttk.Frame(sessao)
    frame.pack(fill="both", expand=True, padx=10, pady=10)

    colunas = ("ID", "Filme", "Sala", "Horário", "Preço (R$)")
    tabela = ttk.Treeview(frame, columns=colunas, show="headings", height=15)

    for col in colunas:
        tabela.heading(col, text=col)
        tabela.column(col, width=150)

    tabela.pack(side="left", fill="both", expand=True)

    scroll = ttk.Scrollbar(frame, orient="vertical", command=tabela.yview)
    tabela.configure(yscrollcommand=scroll.set)
    scroll.pack(side="right", fill="y")

    def carregar_sessoes():
        for item in tabela.get_children():
            tabela.delete(item)
        conexao = conectar()
        if not conexao: return
        cursor = conexao.cursor()
        cursor.execute("""
            SELECT s.id_sessao, f.titulo, s.sala, s.horario, s.preco
            FROM sessoes s
            INNER JOIN cadastro_filme f ON s.id_filme = f.id_filme
            ORDER BY s.horario DESC
        """)
        dados = cursor.fetchall()
        for s in dados:
            # Formata o horário para exibição
            horario_formatado = s[3].strftime("%d/%m/%Y %H:%M")
            tabela.insert("", "end", values=(s[0], s[1], s[2], horario_formatado, s[4]))
        cursor.close()
        conexao.close()

    carregar_sessoes()

    # ========== ADICIONAR SESSÃO ========== #
    def adicionar_sessao():
        add_win = ctk.CTkToplevel(sessao)
        add_win.geometry("400x400")
        add_win.title("Adicionar Sessão")
        add_win.grab_set()

        ctk.CTkLabel(add_win, text="Selecione o Filme:").pack(pady=5)
        conexao = conectar()
        if not conexao: return
        cursor = conexao.cursor()
        cursor.execute("SELECT id_filme, titulo FROM cadastro_filme")
        filmes_db = cursor.fetchall()
        cursor.close()
        conexao.close()

        filmes_dict = {f"{titulo}": id_filme for id_filme, titulo in filmes_db}
        filmes_opcoes = list(filmes_dict.keys())

        combo_filme = ttk.Combobox(add_win, values=filmes_opcoes, width=30)
        combo_filme.pack(pady=5)

        ctk.CTkLabel(add_win, text="Sala:").pack(pady=5)
        sala = ctk.CTkEntry(add_win, width=250)
        sala.pack(pady=5)

        ctk.CTkLabel(add_win, text="Horário (YYYY-MM-DD HH:MM):").pack(pady=5)
        horario = ctk.CTkEntry(add_win, width=250)
        horario.pack(pady=5)

        ctk.CTkLabel(add_win, text="Preço (R$):").pack(pady=5)
        preco = ctk.CTkEntry(add_win, width=250)
        preco.pack(pady=5)

        def salvar_sessao():
            filme_sel = combo_filme.get()
            if filme_sel not in filmes_dict:
                messagebox.showwarning("Atenção", "Selecione um filme válido!")
                return
            id_filme = filmes_dict[filme_sel]
            s_sala = sala.get()
            s_horario = horario.get()
            s_preco = preco.get()

            if not s_sala or not s_horario or not s_preco:
                messagebox.showwarning("Atenção", "Preencha todos os campos!")
                return
            
            try:
                datetime.strptime(s_horario, "%Y-%m-%d %H:%M")
                float(s_preco)
            except ValueError:
                messagebox.showwarning("Atenção", "Formato de Horário ou Preço inválido. Use YYYY-MM-DD HH:MM para horário e um número para preço.")
                return

            conexao = conectar()
            if not conexao: return
            cursor = conexao.cursor()
            try:
                cursor.execute("""
                    INSERT INTO sessoes (id_filme, sala, horario, preco)
                    VALUES (%s, %s, %s, %s)
                """, (id_filme, s_sala, s_horario, s_preco))
                conexao.commit()
                messagebox.showinfo("Sucesso", "Sessão adicionada!")
                add_win.destroy()
                carregar_sessoes()
            except Error as e:
                messagebox.showerror("Erro", f"Erro ao adicionar sessão: {e}")
            finally:
                cursor.close()
                conexao.close()

        ctk.CTkButton(add_win, text="Salvar Sessão", command=salvar_sessao).pack(pady=20)

    # ========== EXCLUIR SESSÃO ========== #
    def excluir_sessao():
        item = tabela.selection()
        if not item:
            messagebox.showwarning("Atenção", "Selecione uma sessão!")
            return
        
        sessao_sel = tabela.item(item)["values"]
        id_sessao = sessao_sel[0]
        filme_titulo = sessao_sel[1]
        horario = sessao_sel[3]

        confirmar = messagebox.askyesno("Confirmação de Exclusão",
                                        f"Tem certeza que deseja excluir a sessão do filme '{filme_titulo}' em {horario} (ID: {id_sessao})?\n"
                                        "Esta ação é irreversível e excluirá todos os ingressos comprados para esta sessão.")
        
        if confirmar:
            conexao = conectar()
            if not conexao: return
            cursor = conexao.cursor()
            try:
                cursor.execute("DELETE FROM sessoes WHERE id_sessao=%s", (id_sessao,))
                conexao.commit()
                carregar_sessoes()
                messagebox.showinfo("Sucesso", "Sessão excluída!")
            except Error as e:
                messagebox.showerror("Erro", f"Erro ao excluir: {e}")
            finally:
                cursor.close()
                conexao.close()

    # ========== EDITAR SESSÃO ========== #
    def editar_sessao():
        item = tabela.selection()
        if not item:
            messagebox.showwarning("Atenção", "Selecione uma sessão para editar!")
            return
        
        sessao_sel = tabela.item(item)["values"]
        id_sessao = sessao_sel[0]
        
        edit_win = ctk.CTkToplevel(sessao)
        edit_win.geometry("400x450")
        edit_win.title(f"Editar Sessão ID: {id_sessao}")
        edit_win.grab_set()

        # Busca o ID do filme original para preencher o combobox
        conexao = conectar()
        if not conexao: return
        cursor = conexao.cursor()
        cursor.execute("SELECT id_filme FROM sessoes WHERE id_sessao = %s", (id_sessao,))
        id_filme_original = cursor.fetchone()[0]
        cursor.execute("SELECT id_filme, titulo FROM cadastro_filme")
        filmes_db = cursor.fetchall()
        cursor.close()
        conexao.close()

        filmes_dict = {f"{titulo}": id_filme for id_filme, titulo in filmes_db}
        filmes_opcoes = list(filmes_dict.keys())
        titulo_filme_original = sessao_sel[1]

        ctk.CTkLabel(edit_win, text="Selecione o Filme:").pack(pady=5)
        combo_filme = ttk.Combobox(edit_win, values=filmes_opcoes, width=30)
        combo_filme.set(titulo_filme_original)
        combo_filme.pack(pady=5)

        ctk.CTkLabel(edit_win, text="Sala:").pack(pady=5)
        sala = ctk.CTkEntry(edit_win, width=250)
        sala.insert(0, sessao_sel[2])
        sala.pack(pady=5)

        ctk.CTkLabel(edit_win, text="Horário (YYYY-MM-DD HH:MM):").pack(pady=5)
        # Converte o formato de exibição (DD/MM/YYYY HH:MM) para o formato de edição (YYYY-MM-DD HH:MM)
        horario_db_format = datetime.strptime(sessao_sel[3], "%d/%m/%Y %H:%M").strftime("%Y-%m-%d %H:%M")
        horario = ctk.CTkEntry(edit_win, width=250)
        horario.insert(0, horario_db_format)
        horario.pack(pady=5)

        ctk.CTkLabel(edit_win, text="Preço (R$):").pack(pady=5)
        preco = ctk.CTkEntry(edit_win, width=250)
        preco.insert(0, sessao_sel[4])
        preco.pack(pady=5)

        def salvar_edicao():
            filme_sel = combo_filme.get()
            if filme_sel not in filmes_dict:
                messagebox.showwarning("Atenção", "Selecione um filme válido!")
                return
            id_filme = filmes_dict[filme_sel]
            s_sala = sala.get()
            s_horario = horario.get()
            s_preco = preco.get()

            if not s_sala or not s_horario or not s_preco:
                messagebox.showwarning("Atenção", "Preencha todos os campos!")
                return
            
            try:
                datetime.strptime(s_horario, "%Y-%m-%d %H:%M")
                float(s_preco)
            except ValueError:
                messagebox.showwarning("Atenção", "Formato de Horário ou Preço inválido. Use YYYY-MM-DD HH:MM para horário e um número para preço.")
                return

            conexao = conectar()
            if not conexao: return
            cursor = conexao.cursor()
            try:
                cursor.execute("""
                    UPDATE sessoes SET id_filme=%s, sala=%s, horario=%s, preco=%s
                    WHERE id_sessao=%s
                """, (id_filme, s_sala, s_horario, s_preco, id_sessao))
                conexao.commit()
                messagebox.showinfo("Sucesso", "Sessão atualizada com sucesso!")
                edit_win.destroy()
                carregar_sessoes()
            except Error as e:
                messagebox.showerror("Erro", f"Erro ao atualizar sessão: {e}")
            finally:
                cursor.close()
                conexao.close()

        ctk.CTkButton(edit_win, text="Salvar Alterações", command=salvar_edicao).pack(pady=20)

    frame_botoes = ctk.CTkFrame(sessao)
    frame_botoes.pack(pady=10)
    ctk.CTkButton(frame_botoes, text="Atualizar Lista", command=carregar_sessoes).pack(side="left", padx=5)
    ctk.CTkButton(frame_botoes, text="Adicionar Sessão", command=adicionar_sessao).pack(side="left", padx=5)
    ctk.CTkButton(frame_botoes, text="Editar Sessão Selecionada", command=editar_sessao).pack(side="left", padx=5)
    ctk.CTkButton(frame_botoes, text="Excluir Sessão Selecionada", command=excluir_sessao).pack(side="left", padx=5)

# =================== GESTÃO DE PRODUTOS (CONCESSÃO) =================== #
def abrir_gestao_produtos():
    produtos = ctk.CTkToplevel()
    produtos.geometry("700x500")
    produtos.title("Gestão de Produtos (Concessão)")
    produtos.grab_set()

    ctk.CTkLabel(produtos, text="Produtos Cadastrados",
                 font=ctk.CTkFont(size=20, weight="bold")).pack(pady=10)

    frame = ttk.Frame(produtos)
    frame.pack(fill="both", expand=True, padx=10, pady=10)

    colunas = ("ID", "Nome", "Descrição", "Preço (R$)", "Estoque")
    tabela = ttk.Treeview(frame, columns=colunas, show="headings", height=15)

    for col in colunas:
        tabela.heading(col, text=col)
        tabela.column(col, width=120)

    tabela.pack(side="left", fill="both", expand=True)

    scroll = ttk.Scrollbar(frame, orient="vertical", command=tabela.yview)
    tabela.configure(yscrollcommand=scroll.set)
    scroll.pack(side="right", fill="y")

    def carregar_produtos():
        for item in tabela.get_children():
            tabela.delete(item)
        conexao = conectar()
        if not conexao: return
        cursor = conexao.cursor()
        cursor.execute("SELECT id_produto, nome, descricao, preco, estoque FROM produtos")
        dados = cursor.fetchall()
        for p in dados:
            tabela.insert("", "end", values=p)
        cursor.close()
        conexao.close()

    carregar_produtos()

    # ========== ADICIONAR PRODUTO ========== #
    def adicionar_produto():
        add_win = ctk.CTkToplevel(produtos)
        add_win.geometry("400x400")
        add_win.title("Adicionar Produto")
        add_win.grab_set()

        ctk.CTkLabel(add_win, text="Nome:*").pack(pady=5)
        nome = ctk.CTkEntry(add_win, width=250)
        nome.pack(pady=5)

        ctk.CTkLabel(add_win, text="Descrição:").pack(pady=5)
        descricao = ctk.CTkEntry(add_win, width=250)
        descricao.pack(pady=5)

        ctk.CTkLabel(add_win, text="Preço (R$):*").pack(pady=5)
        preco = ctk.CTkEntry(add_win, width=250)
        preco.pack(pady=5)

        ctk.CTkLabel(add_win, text="Estoque:*").pack(pady=5)
        estoque = ctk.CTkEntry(add_win, width=250)
        estoque.pack(pady=5)

        def salvar_produto():
            p_nome = nome.get()
            p_descricao = descricao.get()
            p_preco = preco.get()
            p_estoque = estoque.get()

            if not p_nome or not p_preco or not p_estoque:
                messagebox.showwarning("Atenção", "Preencha todos os campos obrigatórios!")
                return
            
            try:
                float(p_preco)
                int(p_estoque)
            except ValueError:
                messagebox.showwarning("Atenção", "Preço e Estoque devem ser números válidos.")
                return

            conexao = conectar()
            if not conexao: return
            cursor = conexao.cursor()
            try:
                cursor.execute("""
                    INSERT INTO produtos (nome, descricao, preco, estoque)
                    VALUES (%s, %s, %s, %s)
                """, (p_nome, p_descricao, p_preco, p_estoque))
                conexao.commit()
                messagebox.showinfo("Sucesso", "Produto adicionado!")
                add_win.destroy()
                carregar_produtos()
            except Error as e:
                messagebox.showerror("Erro", f"Erro ao adicionar produto: {e}")
            finally:
                cursor.close()
                conexao.close()

        ctk.CTkButton(add_win, text="Salvar Produto", command=salvar_produto).pack(pady=20)

    # ========== EXCLUIR PRODUTO ========== #
    def excluir_produto():
        item = tabela.selection()
        if not item:
            messagebox.showwarning("Atenção", "Selecione um produto!")
            return
        
        produto_sel = tabela.item(item)["values"]
        id_produto = produto_sel[0]
        nome_produto = produto_sel[1]

        confirmar = messagebox.askyesno("Confirmação de Exclusão",
                                        f"Tem certeza que deseja excluir o produto '{nome_produto}' (ID: {id_produto})?\n"
                                        "Esta ação é irreversível.")
        
        if confirmar:
            conexao = conectar()
            if not conexao: return
            cursor = conexao.cursor()
            try:
                cursor.execute("DELETE FROM produtos WHERE id_produto=%s", (id_produto,))
                conexao.commit()
                carregar_produtos()
                messagebox.showinfo("Sucesso", "Produto excluído!")
            except Error as e:
                messagebox.showerror("Erro", f"Erro ao excluir: {e}")
            finally:
                cursor.close()
                conexao.close()

    # ========== EDITAR PRODUTO ========== #
    def editar_produto():
        item = tabela.selection()
        if not item:
            messagebox.showwarning("Atenção", "Selecione um produto para editar!")
            return
        
        produto_sel = tabela.item(item)["values"]
        id_produto = produto_sel[0]
        
        edit_win = ctk.CTkToplevel(produtos)
        edit_win.geometry("400x400")
        edit_win.title(f"Editar Produto ID: {id_produto}")
        edit_win.grab_set()

        ctk.CTkLabel(edit_win, text="Nome:").pack(pady=5)
        nome = ctk.CTkEntry(edit_win, width=250)
        nome.insert(0, produto_sel[1])
        nome.pack(pady=5)

        ctk.CTkLabel(edit_win, text="Descrição:").pack(pady=5)
        descricao = ctk.CTkEntry(edit_win, width=250)
        descricao.insert(0, produto_sel[2] if produto_sel[2] else "")
        descricao.pack(pady=5)

        ctk.CTkLabel(edit_win, text="Preço (R$):").pack(pady=5)
        preco = ctk.CTkEntry(edit_win, width=250)
        preco.insert(0, produto_sel[3])
        preco.pack(pady=5)

        ctk.CTkLabel(edit_win, text="Estoque:").pack(pady=5)
        estoque = ctk.CTkEntry(edit_win, width=250)
        estoque.insert(0, produto_sel[4])
        estoque.pack(pady=5)

        def salvar_edicao():
            p_nome = nome.get()
            p_descricao = descricao.get()
            p_preco = preco.get()
            p_estoque = estoque.get()

            if not p_nome or not p_preco or not p_estoque:
                messagebox.showwarning("Atenção", "Preencha todos os campos obrigatórios!")
                return
            
            try:
                float(p_preco)
                int(p_estoque)
            except ValueError:
                messagebox.showwarning("Atenção", "Preço e Estoque devem ser números válidos.")
                return

            conexao = conectar()
            if not conexao: return
            cursor = conexao.cursor()
            try:
                cursor.execute("""
                    UPDATE produtos SET nome=%s, descricao=%s, preco=%s, estoque=%s
                    WHERE id_produto=%s
                """, (p_nome, p_descricao, p_preco, p_estoque, id_produto))
                conexao.commit()
                messagebox.showinfo("Sucesso", "Produto atualizado com sucesso!")
                edit_win.destroy()
                carregar_produtos()
            except Error as e:
                messagebox.showerror("Erro", f"Erro ao atualizar produto: {e}")
            finally:
                cursor.close()
                conexao.close()

        ctk.CTkButton(edit_win, text="Salvar Alterações", command=salvar_edicao).pack(pady=20)

    frame_botoes = ctk.CTkFrame(produtos)
    frame_botoes.pack(pady=10)
    ctk.CTkButton(frame_botoes, text="Atualizar Lista", command=carregar_produtos).pack(side="left", padx=5)
    ctk.CTkButton(frame_botoes, text="Adicionar Produto", command=adicionar_produto).pack(side="left", padx=5)
    ctk.CTkButton(frame_botoes, text="Editar Produto Selecionado", command=editar_produto).pack(side="left", padx=5)
    ctk.CTkButton(frame_botoes, text="Excluir Produto Selecionado", command=excluir_produto).pack(side="left", padx=5)

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