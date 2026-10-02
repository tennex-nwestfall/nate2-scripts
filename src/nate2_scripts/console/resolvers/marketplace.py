import urllib.parse

from nate2_scripts.console.resolvers import Arn, Context, Resolver


class MarketplaceResolver(Resolver):
    def get_service_names(self) -> list[str]:
        return ["tennex", "market", "marketplace"]

    def try_resolve_name(self, context: Context, name: str, search: str) -> str | None:
        return None

    def try_resolve_arn(self, context: Context, arn: Arn) -> str | None:
        return None

    def try_resolve_service(
        self, context: Context, service: str, search: str
    ) -> str | None:
        if service not in self.get_service_names():
            return None

        # console errors for regions other than us-east-1
        context.set_region("us-east-1")
        if service == "tennex":
            safe_search = "?text=tennex"
        elif len(search) > 0:
            safe_search = f"?text={urllib.parse.quote_plus(search)}"
        else:
            safe_search = ""

        # using a percent still fails as amazon removes the search string
        # Searching the same string works, but refreshing the page triggers the same console bug
        return f"console.aws.amazon.com/marketplace/search{safe_search}"

    def try_resolve_id(self, context: Context, id: str) -> str | None:
        return None
