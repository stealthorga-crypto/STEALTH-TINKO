import { LoadingState } from "@/components/states/loading-state";

export default function ConsoleLoading() {
  return (
    <div className="space-y-4 p-8">
      <LoadingState label="Loading console" />
      <LoadingState label="Fetching navigation" />
    </div>
  );
}
