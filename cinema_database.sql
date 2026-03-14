CREATE DATABASE IF NOT EXISTS cinema;
USE cinema;

-- =================== CLIENTES =================== --
CREATE TABLE cadastro_cliente (
    id_cliente INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    cpf CHAR(11) NOT NULL UNIQUE,
    senha VARCHAR(255) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    telefone VARCHAR(15),
    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Admin padrão (CPF: 00000000000 / Senha: admin)
INSERT INTO cadastro_cliente (nome, cpf, senha, email, telefone)
VALUES ('Administrador', '00000000000', 'admin', 'admin@cinema.com', NULL);

-- =================== FILMES =================== --
CREATE TABLE cadastro_filme (
    id_filme INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(150) NOT NULL,
    genero VARCHAR(50) NOT NULL,
    duracao INT NOT NULL,
    descricao TEXT NOT NULL,
    imagem VARCHAR(255)
);

-- =================== SESSÕES =================== --
CREATE TABLE sessoes (
    id_sessao INT AUTO_INCREMENT PRIMARY KEY,
    id_filme INT NOT NULL,
    sala VARCHAR(50) NOT NULL,
    horario DATETIME NOT NULL,
    preco DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (id_filme) REFERENCES cadastro_filme(id_filme) ON DELETE CASCADE
);

-- =================== INGRESSOS COMPRADOS =================== --
CREATE TABLE ingressos_comprados (
    id_compra INT AUTO_INCREMENT PRIMARY KEY,
    id_cliente INT NOT NULL,
    id_sessao INT NOT NULL,
    quantidade INT NOT NULL DEFAULT 1,
    data_compra TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_cliente) REFERENCES cadastro_cliente(id_cliente) ON DELETE CASCADE,
    FOREIGN KEY (id_sessao) REFERENCES sessoes(id_sessao) ON DELETE CASCADE
);

-- =================== PRODUTOS (CONCESSÃO) =================== --
CREATE TABLE produtos (
    id_produto INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    descricao VARCHAR(255),
    preco DECIMAL(10, 2) NOT NULL,
    estoque INT NOT NULL DEFAULT 0
);

-- =================== COMPRAS DE PRODUTOS =================== --
CREATE TABLE compras_produtos (
    id_compra_produto INT AUTO_INCREMENT PRIMARY KEY,
    id_cliente INT NOT NULL,
    id_produto INT NOT NULL,
    quantidade INT NOT NULL DEFAULT 1,
    preco_unitario DECIMAL(10, 2) NOT NULL,
    data_compra TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_cliente) REFERENCES cadastro_cliente(id_cliente) ON DELETE CASCADE,
    FOREIGN KEY (id_produto) REFERENCES produtos(id_produto) ON DELETE CASCADE
);

-- =================== DADOS DE EXEMPLO =================== --
INSERT INTO cadastro_filme (titulo, genero, duracao, descricao) VALUES
('Inception', 'Ficção Científica', 148, 'Um ladrão que rouba segredos através dos sonhos.'),
('Interstellar', 'Ficção Científica', 169, 'Uma equipe de exploradores viaja por um buraco de minhoca.'),
('The Dark Knight', 'Ação', 152, 'Batman enfrenta o Coringa em Gotham City.');

INSERT INTO sessoes (id_filme, sala, horario, preco) VALUES
(1, 'Sala 01', DATE_ADD(NOW(), INTERVAL 1 DAY), 28.00),
(1, 'Sala 02', DATE_ADD(NOW(), INTERVAL 2 DAY), 32.00),
(2, 'Sala 01', DATE_ADD(NOW(), INTERVAL 3 DAY), 28.00),
(3, 'Sala 03', DATE_ADD(NOW(), INTERVAL 1 DAY), 25.00);

INSERT INTO produtos (nome, descricao, preco, estoque) VALUES
('Pipoca Grande', 'Pipoca salgada ou doce, tamanho grande', 18.00, 100),
('Pipoca Média', 'Pipoca salgada ou doce, tamanho médio', 14.00, 100),
('Refrigerante 500ml', 'Coca-Cola, Pepsi ou Guaraná', 10.00, 150),
('Água Mineral', 'Garrafa 500ml', 6.00, 200),
('Combo Pipoca+Refri', 'Pipoca grande + Refrigerante 500ml', 25.00, 80);
