import { SearchForm } from "@/components/SearchForm";

export default function HomePage() {
  return (
    <div>
      <section className="hero">
        <h1 className="hero__title">Is it local?</h1>
        <p className="hero__subtitle">
          Search for a business to see whether it&apos;s family-owned, locally owned, independent,
          a franchise, or corporate — so you can decide where your money goes.
        </p>
      </section>
      <SearchForm />
    </div>
  );
}
