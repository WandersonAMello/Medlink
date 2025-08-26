-- Remove tabelas existentes para garantir um ambiente limpo
DROP TABLE IF EXISTS ConsultaStatusLog CASCADE;
DROP TABLE IF EXISTS Consultas CASCADE;
DROP TABLE IF EXISTS Secretarias CASCADE;
DROP TABLE IF EXISTS Medicos CASCADE;
DROP TABLE IF EXISTS Pacientes CASCADE;
DROP TABLE IF EXISTS Pessoas CASCADE;

-- Tabela central para autenticação e dados comuns
CREATE TABLE Pessoas (
    Id SERIAL PRIMARY KEY,
    Cpf VARCHAR(11) NOT NULL UNIQUE,
    Senha VARCHAR(255) NOT NULL,
    Email VARCHAR(255) UNIQUE,
    TipoPessoa VARCHAR(20) NOT NULL CHECK (TipoPessoa IN ('PACIENTE', 'MEDICO', 'SECRETARIA')),
    DataCriacao TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    DataAtualizacao TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Tabelas especializadas
CREATE TABLE Medicos (
    Id SERIAL PRIMARY KEY,
    NomeCompleto VARCHAR(255) NOT NULL,
    Especialidade VARCHAR(100),
    PessoaId INTEGER NOT NULL UNIQUE,
    FOREIGN KEY (PessoaId) REFERENCES Pessoas(Id) ON DELETE CASCADE
);

CREATE TABLE Secretarias (
    Id SERIAL PRIMARY KEY,
    NomeCompleto VARCHAR(255) NOT NULL,
    PessoaId INTEGER NOT NULL UNIQUE,
    FOREIGN KEY (PessoaId) REFERENCES Pessoas(Id) ON DELETE CASCADE
);

CREATE TABLE Pacientes (
    Id SERIAL PRIMARY KEY,
    NomeCompleto VARCHAR(255) NOT NULL,
    DataNascimento DATE NOT NULL,
    Telefone VARCHAR(20) NOT NULL,
    PessoaId INTEGER NOT NULL UNIQUE,
    FOREIGN KEY (PessoaId) REFERENCES Pessoas(Id) ON DELETE CASCADE
);

CREATE TABLE Consultas (
    Id SERIAL PRIMARY KEY,
    DataHora TIMESTAMP NOT NULL,
    StatusAtual VARCHAR(50) NOT NULL,
    PacienteId INTEGER NOT NULL,
    MedicoId INTEGER NOT NULL,
    DataCriacao TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    DataAtualizacao TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (PacienteId) REFERENCES Pacientes(Id),
    FOREIGN KEY (MedicoId) REFERENCES Medicos(Id)
);

CREATE TABLE ConsultaStatusLog (
    Id SERIAL PRIMARY KEY,
    StatusNovo VARCHAR(50) NOT NULL,
    DataModificacao TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ConsultaId INTEGER NOT NULL,
    PessoaId INTEGER,
    FOREIGN KEY (ConsultaId) REFERENCES Consultas(Id) ON DELETE CASCADE,
    FOREIGN KEY (PessoaId) REFERENCES Pessoas(Id) ON DELETE SET NULL
);


-- ========= TRIGGERS =========

-- 1. FUNÇÃO E TRIGGER PARA ATUALIZAR 'DataAtualizacao'
CREATE OR REPLACE FUNCTION update_data_atualizacao_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.DataAtualizacao = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER trg_update_pessoas_data_atualizacao
BEFORE UPDATE ON Pessoas FOR EACH ROW
EXECUTE FUNCTION update_data_atualizacao_column();

CREATE TRIGGER trg_update_consultas_data_atualizacao
BEFORE UPDATE ON Consultas FOR EACH ROW
EXECUTE FUNCTION update_data_atualizacao_column();


-- 2. FUNÇÃO E TRIGGER PARA LOG DE STATUS DA CONSULTA
CREATE OR REPLACE FUNCTION log_consulta_status_change()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.StatusAtual IS DISTINCT FROM OLD.StatusAtual THEN
        INSERT INTO ConsultaStatusLog(ConsultaId, StatusNovo, DataModificacao, PessoaId)
        VALUES(NEW.Id, NEW.StatusAtual, NOW(), NULL);
    END IF;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER trg_log_consulta_status_change
BEFORE UPDATE ON Consultas FOR EACH ROW
EXECUTE FUNCTION log_consulta_status_change();