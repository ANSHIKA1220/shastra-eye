export default function NotFound() {
  return (
    <div className="screen-glow p-6 text-center">
      <h1 className="text-4xl font-bold terminal-text">404 - Not Found</h1>
      <p className="mt-4 text-lg text-muted-foreground">The page you’re looking for doesn’t exist.</p>
      <a href="/" className="text-primary underline mt-4 inline-block">Go Home</a>
    </div>
  );
}