import { Button } from "@/components/ui/button";

export default function Index() {
  return (
    <div className="screen-glow p-6">
      <h1 className="text-4xl font-bold terminal-text">Welcome to Eye of the Storm</h1>
      <p className="mt-4 text-lg text-muted-foreground">Navigate to <a href="/camera" className="text-primary underline">Camera</a> to start monitoring.</p>
      <Button className="mt-4 control-button" onClick={() => (window.location.href = "/camera")}>
        Go to Camera
      </Button>
    </div>
  );
}