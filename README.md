# Trying_out_Blockchain
Building and learning Blockchain concepts with Python and ReactJS
>> Source code from blog post noted below
그리고 공부한 것들 정리.

## Nonce (Number only used Once)
> Number only used Once (Nonce) is a number hashed inside a single block in blockchain. After a crypto-coin miner re-hash, or figure out the Nonce of a block, cryptocurrency is rewarded as a result. SHA-256 hash is used to create a new nonce.

### Difficulty of Finding a Nonce
> As the difficulty to find the correct nonce increases, so the target value for the hash decreases. This means there have to be more zeros at the start of the hash number. The probability of finding a lower hash value decreases and so miners have to test more nonces. When a miner hashes a block, the hash has to have a value equal to or less than the target number to be successful. [1](https://coincentral.com/what-is-a-nonce-proof-of-work/)
>> Basically, the more zeros there are at the start of the hash, the more difficult it becomes for miners to find the correct hash number because there are lesser number of hash values to match that type of hash value. (0000---- to 000000-- : latter has lesser number combinations, thus more difficult to find the value from of all 2^8 combinations)

## Consensus Mechanism
Used simple Proof of Work as consensus mechanism
### Proof of Work vs Proof of Stack
 - Proof of Work
    - >
 - Proof of Stake
    - > 

## source from [This Post](https://medium.com/@MKGOfficial/build-a-simple-blockchain-cryptocurrency-with-python-django-web-framework-reactjs-f1aebd50b6c)