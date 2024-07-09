import abc
import datetime

class Conta:
    def __init__(self, numero, cliente):
        self._saldo = 0
        self._numero = numero
        self._agencia = "0001"
        self._cliente = cliente
        self._historico = Historico()

    @classmethod
    def nova_conta(cls, cliente, numero):
        return cls(numero, cliente)

    @property
    def saldo(self):
        return self._saldo

    @property
    def numero(self):
        return self._numero

    @property
    def agencia(self):
        return self._agencia

    @property
    def cliente(self):
        return self._cliente

    @property
    def historico(self):
        return self._historico

    def sacar(self, valor):
        saldo = self.saldo
        if valor > 0 and valor <= 500:
            if saldo >= valor:
                self._saldo -= valor
                self.historico.adicionar_transacao(Saque(valor))
                print("Saldo sacado com sucesso!")
                return True
            else:
                print("Saldo insuficiente!")
                return False
        else:
            print("Valor inválido!")
            return False

    def depositar(self, valor):
        if valor > 0:
            self._saldo += valor
            self.historico.adicionar_transacao(Deposito(valor))
            print(f"Valor depositado com sucesso: R${valor:.2f}")
            return True
        else:
            print("Valor inválido!")
            return False

class Cliente:
    def __init__(self, endereco):
        self.endereco = endereco
        self.contas = []

    def realizar_transacao(self, conta, transacao):
        transacao.registrar(conta)

    def adicionar_conta(self, conta):
        self.contas.append(conta)

    def listar_contas(self):
        for conta in self.contas:
            print(f"Conta: {conta.numero}")

class User(Cliente):
    def __init__(self, endereco, nome, data_nascimento, cpf):
        super().__init__(endereco)
        self.nome = nome
        self.data_nascimento = data_nascimento
        self.cpf = cpf

class ContaCorrente(Conta):
    def __init__(self, numero, cliente, limite=500, limite_saques=3):
        super().__init__(numero, cliente)
        self.limite = limite
        self.limite_saques = limite_saques

    def sacar(self, valor):
        numeros_saques = len(
            [transacao for transacao in self.historico.transacoes if transacao["tipo"] == Saque.__name__]
        )

        excedeu_limite = valor > self.limite
        excedeu_saques = numeros_saques >= self.limite_saques

        if excedeu_limite:
            print("Operação falhou! Valor do saque excede o limite.")
        elif excedeu_saques:
            print("Operação falhou! Número de saques excedido.")
        else:
            return super().sacar(valor)
        return False

    def __str__(self):
        return f"""\
Agência: {self.agencia}
C/C: {self.numero}
Titular: {self.cliente.nome}"""

class Historico:
    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self):
        return self._transacoes

    def adicionar_transacao(self, transacao):
        self._transacoes.append(
            {
                "tipo": transacao.__class__.__name__,
                "valor": transacao.valor,
                "data": datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
            }
        )

class Transacao(abc.ABC):
    @property
    @abc.abstractmethod
    def valor(self):
        pass

    @abc.abstractmethod
    def registrar(self, conta):
        pass

class Saque(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        sucesso_transacao = conta.sacar(self.valor)
        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)

class Deposito(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        sucesso_transacao = conta.depositar(self.valor)
        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)

# Funções de suporte
def filtrar_usuario(cpf, usuarios):
    for usuario in usuarios:
        if usuario.cpf == cpf:
            return usuario
    return None

# Simulação
situacao = 1
usuarios = []
contas = []

while situacao == 1:
    print("""
Operações:
[D] - Depositar
[S] - Sacar
[E] - Extrato
[L] - Sair
[C] - Criar usuário
[A] - Criar conta
[LI] - Listar contas
""")
    operacao = input("Escolha uma operação: ").upper()

    if operacao == "D":
        cpf = input("Informe o CPF do usuário: ")
        usuario = filtrar_usuario(cpf, usuarios)
        if usuario:
            numero_conta = input("Informe o número da conta: ")
            conta = next((c for c in usuario.contas if c.numero == numero_conta), None)
            if conta:
                valor = float(input("Informe o valor do depósito: "))
                deposito = Deposito(valor)
                usuario.realizar_transacao(conta, deposito)
            else:
                print("Conta não encontrada!")
        else:
            print("Usuário não encontrado!")
    
    elif operacao == "S":
        cpf = input("Informe o CPF do usuário: ")
        usuario = filtrar_usuario(cpf, usuarios)
        if usuario:
            numero_conta = input("Informe o número da conta: ")
            conta = next((c for c in usuario.contas if c.numero == numero_conta), None)
            if conta:
                valor = float(input("Informe o valor do saque: "))
                saque = Saque(valor)
                usuario.realizar_transacao(conta, saque)
            else:
                print("Conta não encontrada!")
        else:
            print("Usuário não encontrado!")

    elif operacao == "E":
        cpf = input("Informe o CPF do usuário: ")
        usuario = filtrar_usuario(cpf, usuarios)
        if usuario:
            numero_conta = input("Informe o número da conta: ")
            conta = next((c for c in usuario.contas if c.numero == numero_conta), None)
            if conta:
                print(f"Extrato da conta {conta.numero}:")
                for transacao in conta.historico.transacoes:
                    print(f"{transacao['data']} - {transacao['tipo']}: R${transacao['valor']:.2f}")
            else:
                print("Conta não encontrada!")
        else:
            print("Usuário não encontrado!")

    elif operacao == "C":
        nome = input("Informe o nome do usuário: ")
        data_nascimento = input("Informe a data de nascimento (DD/MM/AAAA): ")
        cpf = input("Informe o CPF: ")
        endereco = input("Informe o endereço: ")
        usuario = User(endereco, nome, data_nascimento, cpf)
        usuarios.append(usuario)
        print("Usuário criado com sucesso!")

    elif operacao == "A":
        cpf = input("Informe o CPF do usuário: ")
        usuario = filtrar_usuario(cpf, usuarios)
        if usuario:
            numero_conta = input("Informe o número da conta: ")
            conta = ContaCorrente(numero_conta, usuario)
            usuario.adicionar_conta(conta)
            contas.append(conta)
            print("Conta criada com sucesso!")
        else:
            print("Usuário não encontrado!")

    elif operacao == "LI":
        cpf = input("Informe o CPF do usuário: ")
        usuario = filtrar_usuario(cpf, usuarios)
        if usuario:
            usuario.listar_contas()
        else:
            print("Usuário não encontrado!")

    elif operacao == "L":
        situacao = 0
        print("Saindo...")

    else:
        print("Operação inválida!")
