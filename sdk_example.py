from crowd_sdk import ApiClient
from crowd_sdk.api.default_api import DefaultApi


def main() -> None:
    client = ApiClient()
    api = DefaultApi(client)
    campaigns = api.get_campaigns_campaigns_get()
    print(campaigns)


if __name__ == "__main__":
    main()
