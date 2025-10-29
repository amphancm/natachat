import { Layout } from "@/components/Layout";

export default function Product() {
  return (
    <Layout>
      <div className="p-6">
        <h1 className="text-2xl font-semibold mb-6">Product</h1>
        <div className="bg-card rounded-lg shadow-soft border p-6">
          <p className="text-muted-foreground">Product management features coming soon...</p>
        </div>
      </div>
    </Layout>
  );
}