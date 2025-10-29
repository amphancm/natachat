"use client";

import { useEffect, useState } from "react";
import { Save, Eye, EyeOff } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { Layout } from "@/components/Layout";
import { getSetting, updateSetting, createSetting } from "@/lib/setting";

const DOMAINS = [
  // {
  //   name: "HuggingFace",
  //   value: "huggingface",
  //   models: [
  //     { name: "Llama 3 8B Instruct", api: "meta-llama/Meta-Llama-3-8B-Instruct" },
  //     { name: "Mistral 7B v0.3", api: "mistralai/Mistral-7B-v0.3" },
  //     { name: "Phi 3 Mini 4K Instruct", api: "microsoft/Phi-3-mini-4k-instruct" },
  //     { name: "Qwen 2.5 7B Instruct", api: "Qwen/Qwen2.5-7B-Instruct" },
  //     { name: "Gemma 2 9B", api: "google/gemma-2-9b" },
  //   ],
  // },
  {
    name: "Google",
    value: "google",
    models: [
      { name: "Gemini 1.5 Flash (Free)", api: "gemini-1.5-flash" },
      { name: "Gemini 1.5 Pro", api: "gemini-1.5-pro" },
      { name: "Gemini 2.5 Flash", api: "gemini-2.5-flash" },
    ],
  },
  // {
  //   name: "Together AI",
  //   value: "togetherai",
  //   models: [
  //     { name: "Llama 3.3 70B Turbo", api: "meta-llama/Llama-3.3-70B-Instruct-Turbo" },
  //     { name: "DeepSeek R1 70B", api: "deepseek-ai/DeepSeek-R1-Distill-Llama-70B" },
  //   ],
  // },
];

export default function Settings() {
  const [lineBotSetting, setLineBotSetting] = useState(false);
  const [serverType, setServerType] = useState<"api" | "local">("local");
  const [selectedDomain, setSelectedDomain] = useState(DOMAINS[0].value);
  const [apiKey, setApiKey] = useState("");
  const [modelName, setModelName] = useState(DOMAINS[0].models[0].api);
  const [showApiKey, setShowApiKey] = useState(false);
  const [loading, setLoading] = useState(false);

  const activeDomain = DOMAINS.find((d) => d.value === selectedDomain);

  useEffect(() => {
    (async () => {
      try {
        const setting = await getSetting();
        if (setting) {
          if (setting.domainName) setSelectedDomain(setting.domainName);
          if (setting.modelName) setModelName(setting.modelName);
          if (setting.apiKey) setApiKey(setting.apiKey);
          if (setting.isApi) setServerType("api");
          if (setting.isLocal) setServerType("local");
        }
      } catch {}
    })();
  }, []);

  useEffect(() => {
    if (activeDomain && !activeDomain.models.find((m) => m.api === modelName)) {
      setModelName(activeDomain.models[0].api);
    }
  }, [selectedDomain]);

  async function handleSave() {
    setLoading(true);
    const payload = {
      modelName,
      domainName: selectedDomain,
      apiKey: apiKey || null,
      isApi: serverType === "api",
      isLocal: serverType === "local",
    };
    try {
      const existing = await getSetting();
      if (existing) await updateSetting(payload);
      else await createSetting(payload);
      alert("✅ Setting saved");
    } catch {
      alert("❌ Failed to save");
    } finally {
      setLoading(false);
    }
  }

  return (
    <Layout>
      <div className="p-6 max-w-4xl">
        <h1 className="text-2xl font-semibold mb-6">Settings</h1>
        <div className="space-y-6">
          <div className="bg-card rounded-lg shadow-soft border p-6">
            <div className="flex items-center justify-between">
              <div>
                <Label className="text-base font-medium">Line Bot Setting</Label>
                <p className="text-sm text-muted-foreground">Enable Line Issue Token</p>
              </div>
              <Switch checked={lineBotSetting} onCheckedChange={setLineBotSetting} />
            </div>
          </div>

          <div className="bg-card rounded-lg shadow-soft border p-6">
            <h2 className="text-lg font-medium mb-4">Server Selection</h2>
            <div className="flex gap-4 mb-6">
              <Button
                variant={serverType === "api" ? "default" : "outline"}
                onClick={() => setServerType("api")}
                className={serverType === "api" ? "bg-primary hover:bg-primary/90" : ""}
              >
                API Model
              </Button>
              <Button
                variant={serverType === "local" ? "default" : "outline"}
                onClick={() => setServerType("local")}
                className={serverType === "local" ? "bg-primary hover:bg-primary/90" : ""}
              >
                Local Model
              </Button>
            </div>

            {serverType === "api" && (
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label>Domain</Label>
                  <Select value={selectedDomain} onValueChange={setSelectedDomain}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select Domain" />
                    </SelectTrigger>
                    <SelectContent className="bg-popover">
                      {DOMAINS.map((d) => (
                        <SelectItem key={d.value} value={d.value}>
                          {d.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="apikey">API Key</Label>
                  <div className="relative">
                    <Input
                      id="apikey"
                      value={apiKey}
                      onChange={(e) => setApiKey(e.target.value)}
                      type={showApiKey ? "text" : "password"}
                      placeholder="Enter API Key"
                      className="pr-10"
                    />
                    <button
                      type="button"
                      onClick={() => setShowApiKey(!showApiKey)}
                      className="absolute right-3 top-1/2 transform -translate-y-1/2 text-muted-foreground hover:text-foreground"
                    >
                      {showApiKey ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    </button>
                  </div>
                </div>

                <div className="space-y-2">
                  <Label>Model</Label>
                  <Select value={modelName} onValueChange={setModelName}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select Model" />
                    </SelectTrigger>
                    <SelectContent className="bg-popover">
                      {activeDomain?.models.map((m) => (
                        <SelectItem key={m.api} value={m.api}>
                          {m.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>
            )}

            {serverType === "local" && (
              <div className="space-y-2">
                <Label>Local Model</Label>
                <Select value={modelName} onValueChange={setModelName}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select Local Model" />
                  </SelectTrigger>
                  <SelectContent className="bg-popover">
                    <SelectItem value="llama3-8b">llama3:8b</SelectItem>
                    <SelectItem value="llama3-13b">llama3:13b</SelectItem>
                    <SelectItem value="mistral">Mistral</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            )}

            <Button
              className="mt-6 bg-primary hover:bg-primary/90"
              onClick={handleSave}
              disabled={loading}
            >
              <Save className="h-4 w-4 mr-2" />
              {loading ? "Saving..." : "Save"}
            </Button>
          </div>
        </div>
      </div>
    </Layout>
  );
}
