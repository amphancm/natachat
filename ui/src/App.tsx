import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Login from "./pages/Login";
import Documents from "./pages/Documents";
import UploadFiles from "./pages/UploadFiles";
import SystemPrompt from "./pages/SystemPrompt";
import Product from "./pages/Product";
import UserFeedback from "./pages/UserFeedback";
import Chat from "./pages/Chat";
import Settings from "./pages/Settings";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Login />} />
          <Route path="/documents" element={<Documents />} />
          {/* <Route path="/upload-files" element={<UploadFiles />} /> */}
          <Route path="/system-prompt" element={<SystemPrompt />} />
          {/* <Route path="/product" element={<Product />} />
          <Route path="/user-feedback" element={<UserFeedback />} /> */}
          <Route path="/chat" element={<Chat />} />
          <Route path="/settings" element={<Settings />} />
          {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
