import PageTransition from "@/components/PageTransition";

export default function DocsTemplate({ children }: { children: React.ReactNode }) {
  return <PageTransition>{children}</PageTransition>;
}
