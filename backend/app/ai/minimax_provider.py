import httpx
class MiniMaxProvider:
    def __init__(self,key:str,base_url:str='https://api.minimax.io/v1',model:str='MiniMax-M2.7'):self.key,self.base_url,self.model=key,base_url.rstrip('/'),model
    async def complete(self,system:str,user:str)->str:
        async with httpx.AsyncClient(timeout=12) as client:
            response=await client.post(f'{self.base_url}/text/chatcompletion_v2',headers={'Authorization':f'Bearer {self.key}'},json={'model':self.model,'messages':[{'role':'system','content':system},{'role':'user','content':user}],'temperature':0.4})
            response.raise_for_status();return response.json()['choices'][0]['message']['content']
