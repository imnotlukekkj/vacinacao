import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar";
import { AppSidebar } from "@/components/AppSidebar";
import { Dashboard } from "./pages/Dashboard";
import { Aplicacao } from "./pages/Aplicacao";
import { Distribuicao } from "./pages/Distribuicao";
import { Esavi } from "./pages/Esavi";
import { Qualidade } from "./pages/Qualidade";
import { Sobre } from "./pages/Sobre";
import { NotFound } from "./pages/NotFound";

const queryClient = new QueryClient();

export function App() {
  const queryClient = new QueryClient();
  return (
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <Toaster />
        <Sonner />
        <BrowserRouter>
          <SidebarProvider>
            <div className="flex min-h-screen w-full">
              <AppSidebar />
              <div className="flex-1 flex flex-col">
                <header className="sticky top-0 z-40 border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
                  <div className="flex h-14 items-center px-4">
                    <SidebarTrigger />
                  </div>
                </header>
                <main className="flex-1 p-6">
                  <Routes>
                    <Route path="/" element={<Dashboard />} />
                    <Route path="/aplicacao" element={<Aplicacao />} />
                    <Route path="/distribuicao" element={<Distribuicao />} />
                    <Route path="/qualidade" element={<Qualidade />} />
                    <Route path="/sobre" element={<Sobre />} />
                    <Route path="*" element={<NotFound />} />
                  </Routes>
                </main>
              </div>
            </div>
          </SidebarProvider>
        </BrowserRouter>
      </TooltipProvider>
    </QueryClientProvider>
  );
}

// no default export to enforce named exports
