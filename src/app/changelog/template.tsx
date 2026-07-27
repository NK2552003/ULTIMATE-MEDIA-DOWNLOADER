import PageTransition from "@/components/PageTransition";

export default function ChangelogTemplate({ children }: { children: React.ReactNode }) {
  return <PageTransition>{children}</PageTransition>;
}
