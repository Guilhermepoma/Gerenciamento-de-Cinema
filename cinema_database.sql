CREATE DATABASE cinema;
USE cinema;

CREATE TABLE cadastro_filme (
    id_filme INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(100) NOT NULL,
    genero VARCHAR(50) NOT NULL,
    duracao INT NOT NULL,
    descricao VARCHAR(200) NOT NULL
);

CREATE TABLE sessao_filme (
    id_sessao INT AUTO_INCREMENT PRIMARY KEY,
    id_filme INT NOT NULL,
    data_sessao DATE NOT NULL,
    preco DECIMAL(6,2) NOT NULL,
    FOREIGN KEY (id_filme) REFERENCES cadastro_filme(id_filme)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE cadastro_cliente (
    id_cliente INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    cpf CHAR(11) NOT NULL UNIQUE,
    email VARCHAR(50) NOT NULL UNIQUE, 
    telefone VARCHAR(20)
);

CREATE TABLE compra_ingresso (
    id_compra INT AUTO_INCREMENT PRIMARY KEY,
    id_cliente INT NOT NULL,
    id_sessao INT NOT NULL,
    quantidade INT DEFAULT 1,
    valor_total DECIMAL(8,2),
    data_compra TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_cliente) REFERENCES cadastro_cliente(id_cliente)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (id_sessao) REFERENCES sessao_filme(id_sessao)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE INDEX idx_sessao_filme_id_filme ON sessao_filme(id_filme);
CREATE INDEX idx_compra_id_cliente ON compra_ingresso(id_cliente);
CREATE INDEX idx_compra_id_sessao ON compra_ingresso(id_sessao);

CREATE OR REPLACE VIEW view_compras AS
SELECT 
    ci.id_compra,
    c.nome AS cliente,
    f.titulo AS filme,
    s.data_sessao,
    ci.quantidade,
    ci.valor_total,
    ci.data_compra
FROM compra_ingresso ci
JOIN cadastro_cliente c ON ci.id_cliente = c.id_cliente
JOIN sessao_filme s ON ci.id_sessao = s.id_sessao
JOIN cadastro_filme f ON s.id_filme = f.id_filme;