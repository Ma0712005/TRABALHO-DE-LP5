import sqlite3


class SistemaIntegradoUigeDB:
    """Sistema Central com Base de Dados SQLite para a Província do Uíge."""

    def __init__(self, nome_bd="uige_saude.db"):
        self.conn = sqlite3.connect(nome_bd)
        self.cursor = self.conn.cursor()
        self.criar_tabelas()

    def criar_tabelas(self):
        """Cria as tabelas necessárias na base de dados, caso não existam."""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS unidades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                tipo TEXT NOT NULL,
                municipio TEXT NOT NULL
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS pacientes (
                bi TEXT PRIMARY KEY,
                nome TEXT NOT NULL,
                data_nascimento TEXT NOT NULL
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS historico (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bi_paciente TEXT,
                unidade TEXT,
                medico TEXT,
                diagnostico TEXT,
                tratamento TEXT,
                data TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (bi_paciente) REFERENCES pacientes (bi)
            )
        ''')
        self.conn.commit()

    def cadastrar_unidade(self, nome, tipo, municipio):
        self.cursor.execute('''
            INSERT INTO unidades (nome, tipo, municipio) VALUES (?, ?, ?)
        ''', (nome, tipo, municipio))
        self.conn.commit()
        print(f"\n[SUCESSO] Unidade '{nome}' registada com sucesso!")

    def cadastrar_paciente(self, nome, bi, data_nascimento):
        try:
            self.cursor.execute('''
                INSERT INTO pacientes (bi, nome, data_nascimento) VALUES (?, ?, ?)
            ''', (bi, nome, data_nascimento))
            self.conn.commit()
            print(f"\n[SUCESSO] Paciente '{nome}' registado com sucesso!")
        except sqlite3.IntegrityError:
            print(f"\n[AVISO] O paciente com o BI '{bi}' já se encontra registado.")

    def registrar_atendimento(self, bi_paciente, nome_unidade, medico, diagnostico, tratamento):
        # Verificar se o paciente existe
        self.cursor.execute('SELECT nome FROM pacientes WHERE bi = ?', (bi_paciente,))
        paciente = self.cursor.fetchone()

        if paciente:
            self.cursor.execute('''
                INSERT INTO historico (bi_paciente, unidade, medico, diagnostico, tratamento)
                VALUES (?, ?, ?, ?, ?)
            ''', (bi_paciente, nome_unidade, medico, diagnostico, tratamento))
            self.conn.commit()
            print(f"\n[SUCESSO] Atendimento registado para o paciente {paciente[0]}.")
        else:
            print(f"\n[ERRO] Paciente com BI '{bi_paciente}' não encontrado no sistema. Registe o paciente primeiro.")

    def consultar_historico_global(self, bi_paciente):
        # Buscar dados do paciente
        self.cursor.execute('SELECT nome, data_nascimento FROM pacientes WHERE bi = ?', (bi_paciente,))
        paciente = self.cursor.fetchone()

        if paciente:
            nome, data_nascimento = paciente
            print(f"\n==================================================")
            print(f" HISTÓRICO CLÍNICO INTEGRADO - PROVÍNCIA DO UÍGE")
            print(f"==================================================")
            print(f" Nome: {nome} | BI: {bi_paciente} | Data Nasc.: {data_nascimento}")
            print(f"--------------------------------------------------")

            # Buscar histórico clínico
            self.cursor.execute('''
                SELECT unidade, medico, diagnostico, tratamento, data 
                FROM historico WHERE bi_paciente = ?
            ''', (bi_paciente,))
            registros = self.cursor.fetchall()

            if not registros:
                print(" Nenhum registo clínico encontrado.")
            else:
                for i, reg in enumerate(registros, 1):
                    print(f" [{i}] Data/Hora: {reg[4]}")
                    print(f"     Unidade: {reg[0]}")
                    print(f"     Médico(a): {reg[1]}")
                    print(f"     Diagnóstico: {reg[2]}")
                    print(f"     Tratamento: {reg[3]}")
                    print(f"--------------------------------------------------")
        else:
            print(f"\n[ERRO] Paciente com BI '{bi_paciente}' não encontrado.")

    def fechar_conexao(self):
        self.conn.close()


def menu():
    db = SistemaIntegradoUigeDB()

    while True:
        print("\n=== DIREÇÃO PROVINCIAL DA SAÚDE DO UÍGE ===")
        print("1. Registar Unidade de Saúde")
        print("2. Registar Paciente")
        print("3. Registar Atendimento (Consulta/Histórico)")
        print("4. Consultar Histórico Clínico de Paciente")
        print("5. Sair")

        opcao = input("\nEscolha uma opção (1-5): ").strip()

        if opcao == "1":
            nome = input("Nome da Unidade (ex: Hospital Provincial do Uíge): ")
            tipo = input("Tipo (ex: Hospital Geral / Centro de Saúde): ")
            municipio = input("Município (ex: Uíge, Negage, Maquela): ")
            db.cadastrar_unidade(nome, tipo, municipio)

        elif opcao == "2":
            nome = input("Nome completo do paciente: ")
            bi = input("Número do BI: ")
            data_nasc = input("Data de nascimento (DD/MM/AAAA): ")
            db.cadastrar_paciente(nome, bi, data_nasc)

        elif opcao == "3":
            bi = input("BI do paciente: ")
            unidade = input("Nome da Unidade de Saúde onde ocorreu o atendimento: ")
            medico = input("Nome do(a) Médico(a): ")
            diagnostico = input("Diagnóstico: ")
            tratamento = input("Tratamento / Prescrição: ")
            db.registrar_atendimento(bi, unidade, medico, diagnostico, tratamento)

        elif opcao == "4":
            bi = input("Digite o BI do paciente para consultar o histórico: ")
            db.consultar_historico_global(bi)

        elif opcao == "5":
            print("\nA encerrar o sistema provincial. Até breve!")
            db.fechar_conexao()
            break
        else:
            print("\n[ERRO] Opção inválida! Escolha um número de 1 a 5.")


if __name__ == "__main__":
    menu()