import Link from "next/link";

export default function NotFound() {
  return (
    <div className="hero">
      <h1 className="hero__title">Not found</h1>
      <p className="hero__subtitle">
        We couldn&apos;t find that business. It may have been removed or the link is incorrect.
      </p>
      <Link href="/" className="button button--primary">
        Back to search
      </Link>
    </div>
  );
}
