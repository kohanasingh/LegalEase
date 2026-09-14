import AnalysisView from "./AnalysisView";

export default async function AnalyzePage(props: PageProps<"/analyze/[docId]">) {
  const { docId } = await props.params;
  return <AnalysisView docId={docId} />;
}
