export type CatalogProduct = {
  id: string;
  title: string;
  handle: string;
  status: string;
  featuredImageUrl: string | null;
  price: string | null;
};

const shopDomain = process.env.SHOPIFY_SHOP_DOMAIN;
const adminToken = process.env.SHOPIFY_ADMIN_ACCESS_TOKEN;

export async function searchCatalog(query: string): Promise<{ configured: boolean; products: CatalogProduct[]; message: string }> {
  if (!shopDomain || !adminToken) {
    return {
      configured: false,
      products: [],
      message: "Shopify catalog read-only access is not configured yet. No Shopify request was made.",
    };
  }

  const response = await fetch(`https://${shopDomain}/admin/api/2026-07/graphql.json`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-Shopify-Access-Token": adminToken,
    },
    body: JSON.stringify({
      query: `query SearchCampaignCatalog($query: String!) {
        products(first: 12, query: $query) {
          nodes {
            id title handle status
            featuredImage { url }
            variants(first: 1) { nodes { price } }
          }
        }
      }`,
      variables: { query },
    }),
  });

  if (!response.ok) throw new Error(`Shopify catalog request failed with HTTP ${response.status}.`);
  const body = await response.json() as { data?: { products?: { nodes?: Array<Record<string, unknown>> } }; errors?: Array<{ message: string }> };
  if (body.errors?.length) throw new Error(body.errors.map(error => error.message).join(" "));

  const products = body.data?.products?.nodes?.map(product => {
    const variants = product.variants as { nodes?: Array<{ price?: string }> } | undefined;
    const image = product.featuredImage as { url?: string } | null;
    return {
      id: String(product.id),
      title: String(product.title),
      handle: String(product.handle),
      status: String(product.status),
      featuredImageUrl: image?.url ?? null,
      price: variants?.nodes?.[0]?.price ?? null,
    };
  }) ?? [];

  return { configured: true, products, message: "Read-only Shopify catalog results." };
}
