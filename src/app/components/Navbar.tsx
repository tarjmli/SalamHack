import Link from "next/link";

const Navbar = () => {
  return (
    <nav className="p-4 bg-blue-600 text-white flex justify-between">
      <h1 className="text-lg font-bold">MyApp</h1>
      <div>
        <Link href="/" className="mr-4">
          Home
        </Link>
        <Link href="/auth" className="mr-4">
          Auth
        </Link>
      </div>
    </nav>
  );
};

export default Navbar;
