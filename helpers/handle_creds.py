def load_correct_creds(creds):
    #if TEST_MODE:
    #    return creds['test']['key'], creds['test']['secret'], creds['test']['passphrase']
    #else:
    return creds['prod']['key'], creds['prod']['secret'], creds['prod']['passphrase']





def test_api_key(client):
    """Checks to see if API keys supplied returns errors

    Args:
        client (class): binance client class
        BinanceAPIException (clas): binance exeptions class

    Returns:
        bool | msg: true/false depending on success, and message
    """
    try:
        client.get_account_list()
        return True, "API key validated succesfully"
    
    except Exception as e:
        return False, f"Fallback exception occured:\n{e}"
