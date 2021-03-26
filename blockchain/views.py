from django.shortcuts import render
import datetime
import hashlib
import json
from uuid import uuid4
import socket
from urllib.parse import urlparse
from django.http import JsonResponse, HttpResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt 

"""
    Basic features of a blockchain.
    
"""
class Blockchain:

    """
        블록체인을 초기화 시킨다. 
        실제 체인, 거래 내역, 해당 블록체인을 사용 중인 노드 (사용자) 들의 netloc 기록을 초기화.
        제네시스 블록 (블록체인의 맨 첫 블록) 을 생성한다. 
    """
    def __init__(self):
        self.chain = []
        self.transactions = []
        self.nodes = set()
        self.create_block(nonce = 1, previous_hash = '0')

    """
        블록체인의 블록을 만든다.
        블록헤더에서는 
            블록의 인덱스 (체인에서의 위치)   -> 'index'
            생성 시간                    -> 'timestamp'
            생성된 블록의 고유 헤쉬 값       -> 'nonce'
            이전 블록의 고유 해쉬 값        -> 'previous hash'
            거래 내역 (각 전송마다 초기화 됨) -> 'transactions'
        거래 기록은 초기화 한다. (이전 블록과 현재 블록의 거래 기록만 저장) 
        생성 된 블록은 체인에 추가된다.
    """
    def create_block(self, nonce, previous_hash):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': str(datetime.datetime.now()),
            'nonce': nonce,
            'previous_hash': previous_hash,
            'transactions' : self.transactions
        }
        self.transactions = []
        self.chain.append(block)

        return block

    """
        이전 블록을 해당 체인에서 가져온다
    """
    def get_previous_block(self):
        return self.chain[-1]

    """
        증명 메커니즘 중에서 Proof os Work 을 사용했다. 
        해쉬 값의 첫 4개의 패턴이 '0000'으로 시작 하는 nonce 값을 찾는다.
        숫자 '0' 의 길이가 길어 질 수록 해당 패턴에 알맞는 해쉬 값을 갖은 nonce 값을 찾기 어려워 진다.
    """
    def proof_of_work(self, previous_nonce):
        new_nonce = 1
        check_nonce = False
        while check_nonce is False:
            hash_operation = hashlib.sha256(str(new_nonce**2 - previous_nonce**2).encode()).hexdigest()
            if hash_operation[:4] == '0000':
                check_nonce = True
            else:
                new_nonce += 1
        
        return new_nonce

    """
        previous_hash 를 찾기 위한 블록 전체를 해쉬 한 값이다.
    """
    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys = True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    """
        해당 블록체인의 투명성을 증명한다.
        현재 블록의 이전 블록 해쉬 기록과 이전 블록의 해쉬 값이 일치하는 지 확인한다.
        블록을 생성 할 때의 해쉬 알고리즘을 사용하여 해당 값이 패턴과 일치하는 지 확인한다.
        일치하지 않으면 해당 체인은 유효하지 않으므로 False 를 반환한다.
        이렇게 전체 블록체인의 유효성 검사를 한다.
    """
    def is_chain_valid(self, chain):
        previous_block = chain[0]
        block_index = 1

        while block_index < len(chain):
            block = chain[block_index] 
            if block['previous_hash'] != self.hash(previous_block):
                return False
            previous_nonce = previous_block['nonce']
            nonce = block['nonce']
            hash_operation = hashlib.sha256(str(nonce**2 - previous_nonce**2).encode()).hexdigest()
            if(hash_operation[:4] != '0000'):
                return False
            previous_block = block
            block_index += 1
        return True

    """
        화폐의 거래 내용을 기록한다. 
        이 기록은 블록이 생성 되면 초기화 된다.
    """
    def add_transaction(self, sender, receiver, amount, time):
        self.transactions.append({
            'sender' : sender,
            'receiver' : receiver,
            'amount' : amount,
            'time' : str(datetime.datetime.now())
        })
        previous_block = self.get_previous_block()

        return previous_block['index'] + 1

    """"
        블록체인 네트워크에 접속 되어 있는 유저 netloc 값을 추가 한다.
    """
    def add_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    """
        블록체인의 네트워크 사이에 가장 최신화된 체인으로 현재 블록체인을 갈아 낀다.
    """
    def replace_chain(self):
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)
        for node in network:
            response = requests.get(f'http://{node}/get_chain')
            if(response.status_code == 200):
                length = response.json()['length']
                chain = response.json()['chain']
                if(length > max_length and self.is_chain_valid(chain)):
                    max_length = length
                    longest_chain = chain

        if(longest_chain):
            self.chain = longest_chain
            return True

        return False

""""
    블록체인을 활성화 하고, 현재 네트워크의 값을 가져와 node_address 로 저장
    root_node 는 임의의 해쉬 값으로 정해 논다.
"""
blockchain = Blockchain()
node_address = str(uuid4()).replace('-', '')
root_node = 'e36f0158f0aed45b3bc755dc52ed4560d'

"""
    REST API 의 GET request 에서 '/mine_block' 이 호출 되면
    블록을 채굴(mine) 한다.
    채굴 시 체인의 가장 최근 블록의 nonce 값을 활용해 해쉬 값을 찾고 PoW을 진행한다.
    블록을 생성하고 체인에 추가 후 JSON response 를 반환한다.
"""
def mine_block(request):
    if(request.method) == 'GET':
        previous_block = blockchain.get_previous_block()
        previous_nonce = previous_block['nonce']
        nonce = blockchain.proof_of_work(previous_nonce)
        previous_hash = blockchain.hash(previous_block)
        blockchain.add_transaction(sender = root_node, receiver = node_address, amount = 1.15, time=str(datetime.datetime.now()))
        block = blockchain.create_block(nonce, previous_hash)
        response = {
            'message' : 'Block has been mined',
            'index' : block['index'],
            'timestamp' : block['timestamp'],
            'nonce' : block['nonce'],
            'previous_hash' : block['previous_hash'],
            'transactions' : block['transactions']
        }

    return JsonResponse(response)

"""
    REST API 의 GET request 에서 '/get_chain' 이 호출 되면
    현재 네트워크에 생성되어 진 체인의 정보를 JSON response 로 반환한다.
"""
def get_chain(request):
    if request.method == 'GET':
        response = {
            'chain' : blockchain.chain,
            'length' : len(blockchain.chain)
        }
    return JsonResponse(response)

"""
    REST API 의 GET request 에서 '/is_valid' 이 호출 되면
    블록체인의 유효성 검사 후 결과를 Response 로 반환한다.
"""
def is_valid(request):
    if request.method == 'GET':
        is_valid = blockchain.is_chain_valid(blockchain.chain)
        if(is_valid):
            response = {'message': 'Blockchain Valid'}
        else:
            response = {'message': 'Houston, we have a problem : chain Invalid'}
        return JsonResponse(response)

"""
    @csrf_exempt : Cross Site Request Forgery protection turned off
    Sends a POST response to the blockchain network during currency transaction.
"""
@csrf_exempt
def add_transaction(request):
    if(request.method == 'POST'):
        received_json = json.loads(request.body)
        transaction_keys = ['sender', 'receiver', 'amount', 'time']
        if not all(key in received_json for key in transaction_keys):
            return 'Some element in transaction is missing', HttpResponse(status=400)
        index = blockchain.add_transaction(received_json['sender'], received_json['receiver'], received_json['amount'], received_json['time'])
        response = {'message' : f'This transaction will be added to the block {index}'}
    return JsonResponse(response)

"""
    Sends a POST response to blockchain network to add the node created after currency
"""
@csrf_exempt
def connect_node(request):
    if(request.method == 'POST'):
        received_json = json.loads(request.body)
        nodes = received_json.get('nodes')
        if(nodes is None):
            return 'No node', HttpResponse(status=400)
        for node in nodes:
            blockchain.add_node(node)
    response = {
            'message': 'All the nodes are now connected. Coin contains following nodes',
            'total_nodes' : list(blockchain.nodes)
        }    
    return JsonResponse(response)

"""
    네트워크에서 가장 긴 체인으로 최신화한다.
    replace_chain() -> 최신화를 진행 했으면 참 / 이미 제일 긴 체인이 었다면 거짓을 반환한다.
    JSON response 를 반환한다. 
"""
def replace_chain(request):
    if request.method == 'GET':
        is_chain_replaced = blockchain.replace_chain()
        if is_chain_replaced:
            response = {
                'message': 'The nodes had different chains. Chain replaced by longest one',
                'new_chain' : blockchain.chain
            }
        else:
            response = {
                'message': 'All good. Longest Chain is shown',
                'actual_chain' : blockchain.chain
            }

    return JsonResponse(response)