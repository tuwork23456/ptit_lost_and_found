import React from "react";
import LatestNews from "../components/LatestNews";

const Home = () => {
  return (
    <div className="w-full bg-[#f8fafc] min-h-screen relative overflow-hidden">
      {/* Decorative Background Blobs */}
      <div className="absolute top-[-10%] left-[-5%] w-[40%] h-[40%] rounded-full bg-gradient-to-r from-red-400 to-rose-300 mix-blend-multiply filter blur-[100px] opacity-30 animate-float-slow pointer-events-none z-0"></div>
      <div className="absolute top-[20%] right-[-10%] w-[35%] h-[40%] rounded-full bg-gradient-to-l from-orange-300 to-red-300 mix-blend-multiply filter blur-[120px] opacity-20 animate-float-medium pointer-events-none z-0"></div>
      <div className="absolute -bottom-32 left-[20%] w-[50%] h-[50%] rounded-full bg-gradient-to-t from-rose-200 to-pink-200 mix-blend-multiply filter blur-[150px] opacity-40 animate-pulse-bg pointer-events-none z-0"></div>

      <div className="xl:px-[250px] px-4 md:px-10 mx-auto py-4 md:py-8 relative z-10 w-full min-h-screen flex flex-col justify-center">
        <div className="w-full mb-10">
          <LatestNews />
        </div>
      </div>
    </div>
  );
};

export default Home;
