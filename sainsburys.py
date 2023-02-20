
import requests
import json

def main():
    AT = get_access_token()
    shop_list = get_shop_list(AT)
    parsed_stores = parse_stores(shop_list)
    store = get_correct_store(parsed_stores)
    info = get_info(store[0], AT, store[1], store[2])
    print(info)
    
def get_access_token():
    AT_request_headers = {"authority":"stockchecker.sainsbury.co.uk","accept":"application/json"}
    AT_request = requests.get('https://stockchecker.sainsburys.co.uk/api/authorisation/token', headers=AT_request_headers)
    AT=AT_request.json()["access_token"]
    return AT
    
    

def get_shop_list(AT):
    shop=input("\nWhat shop are you searching for?: ")
    shop = shop.rsplit()
    query_link="https://stockchecker.sainsburys.co.uk/api/store/search?store_type=main,local&complete="
    for i in shop:
        if i == shop[0]:
            query_link = query_link+f"{i}"
        else:
            query_link = query_link+f"+{i}"
    
    shop_query_headers={"authorization": f"Bearer {AT}"}
    shop_query = requests.get(query_link, headers=shop_query_headers).json()
    return shop_query
    

def parse_stores(shop_query):
    names_ids={}
    if len(shop_query["results"]) == 0:
        print("No results found. Please check for misspelt words/typos.")
        exit()
    for i in shop_query["results"]:
        names_ids.update({i["other_name"]:i["code"]})
    return names_ids

def get_correct_store(names_ids):
    chosen={}
    key=1
    for i in names_ids:
        chosen.update({key:i})
        key+=1
    

    if len(chosen) < 5:
        x=len(chosen)
    else:
        x=5

    print("\n")
    for i in range(x):
        print(f"{i+1}: "+chosen[i+1])
    print("\n")

    correct_store = int(input("Which store are you referring to?: "))
    try:
        chosen_store_id=names_ids[chosen[correct_store]]
    except Exception as err:
        if err == TypeError:
            print("This store doesnt stock Prime.")
    return chosen_store_id, chosen, correct_store

def get_info(chosen_store_id, AT, chosen, correct_store):
    product_payload = {"query":"query searchProductsByName($store: Int!, $query: String!, $pageNumber: Int!) {\n  productSearch(storeCode: $store, query: $query) {\n    storeProducts {\n      sku\n      description\n      images {\n        uri\n      }\n      store(storeCode: $store) {\n        retailPrice\n        supplyStatusDescription\n        stock {\n          onHand\n        }\n      }\n    }\n  }\n}\n",
                        "variables":{"store":chosen_store_id,"query":"prime hydration","pageNumber":1}}
    product_payload_ksi= {"query":"query searchProductsByName($store: Int!, $query: String!, $pageNumber: Int!) {\n  productSearch(storeCode: $store, query: $query) {\n    storeProducts {\n      sku\n      description\n      images {\n        uri\n      }\n      store(storeCode: $store) {\n        retailPrice\n        supplyStatusDescription\n        stock {\n          onHand\n        }\n      }\n    }\n  }\n}\n",
                        "variables":{"store":chosen_store_id,"query":"8154398","pageNumber":1}}
                        
    get_product_headers={"authorization": f"Bearer {AT}","content-type":"application/json"}
    get_product=requests.post("https://stockchecker.sainsburys.co.uk/api/products/search", data=json.dumps(product_payload), headers=get_product_headers).json()
    get_product_ksi=requests.post("https://stockchecker.sainsburys.co.uk/api/products/search", data=json.dumps(product_payload_ksi), headers=get_product_headers).json()
    info={}
    try:
        for i in range(len(get_product["data"]["productSearch"]["storeProducts"])):
            info.update({get_product["data"]["productSearch"]["storeProducts"][i]["description"]:int(get_product["data"]["productSearch"]["storeProducts"][i]["store"]["stock"]["onHand"])})
    except TypeError:
        print("\nStock is not loaded at this store.")
        exit()
    info_printable=f"\nInfo for {chosen[correct_store]}: \n\n"

    for i in info:
        info_printable=info_printable+f"Product: {i}: On Hand: {info[i]} \n"
    ksiname= get_product_ksi["data"]["productSearch"]["storeProducts"][0]["description"]
    ksistock=int(get_product["data"]["productSearch"]["storeProducts"][0]["store"]["stock"]["onHand"])
    info_printable=info_printable+f"Product: {ksiname}: On Hand: {ksistock} "
    return info_printable

if __name__ == "__main__":
    main()







    

