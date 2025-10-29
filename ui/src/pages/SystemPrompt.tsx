import { useEffect, useState } from "react";
import { Save } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Slider } from "@/components/ui/slider";
import { Layout } from "@/components/Layout";
import { getSetting, updateSetting, createSetting } from "@/lib/setting";

export default function SystemPrompt() {
  const [temperature, setTemperature] = useState([0.7]);
  const [systemPrompt, setSystemPrompt] = useState("");
  const [loading, setLoading] = useState(false);

  // โหลดค่า Setting จาก API
  useEffect(() => {
    (async () => {
      try {
        const setting = await getSetting();
        if (setting) {
          if (setting.temperature !== null && setting.temperature !== undefined) {
            setTemperature([setting.temperature]);
          }
          if (setting.systemPrompt) {
            setSystemPrompt(setting.systemPrompt);
          }
        }
      } catch (error) {
        console.error("Failed to load setting:", error);
      }
    })();
  }, []);

  // กด Save แล้วเรียก API
  async function handleSave() {
    setLoading(true);
    try {
      const payload = {
        temperature: temperature[0],
        systemPrompt: systemPrompt || null,
      };
      const existing = await getSetting();
      if (existing) {
        await updateSetting(payload);
      } else {
        await createSetting(payload);
      }
      alert("✅ Setting saved successfully");
    } catch (error) {
      console.error(error);
      alert("❌ Failed to save setting");
    } finally {
      setLoading(false);
    }
  }

  return (
    <Layout>
      <div className="p-6 max-w-4xl">
        <h1 className="text-2xl font-semibold mb-6">System Prompt</h1>

        <div className="space-y-8">
          {/* Temperature */}
          <div className="space-y-4">
            <h2 className="text-lg font-medium">Parameters</h2>
            <div className="bg-card rounded-lg shadow-soft border p-6">
              <div className="space-y-4">
                <Label htmlFor="temperature" className="text-base">
                  Temperature
                </Label>
                <div className="space-y-3">
                  <div className="flex items-center gap-2">
                    <span className="bg-primary text-primary-foreground px-2 py-1 rounded text-sm font-medium">
                      {temperature[0].toFixed(1)}
                    </span>
                  </div>
                  <Slider
                    id="temperature"
                    min={0}
                    max={1}
                    step={0.1}
                    value={temperature}
                    onValueChange={setTemperature}
                    className="w-full max-w-md"
                  />
                </div>
              </div>
            </div>
          </div>

          {/* System Prompt */}
          <div className="space-y-4">
            <h2 className="text-lg font-medium">System Prompt</h2>
            <div className="bg-card rounded-lg shadow-soft border p-6">
              <div className="space-y-4">
                <Textarea
                  placeholder="Enter System Prompt"
                  value={systemPrompt}
                  onChange={(e) => setSystemPrompt(e.target.value)}
                  className="min-h-48 resize-none"
                />
                <Button
                  onClick={handleSave}
                  disabled={loading}
                  className="bg-primary hover:bg-primary/90"
                >
                  <Save className="h-4 w-4 mr-2" />
                  {loading ? "Saving..." : "Save"}
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}
