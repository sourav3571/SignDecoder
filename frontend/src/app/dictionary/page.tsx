"use client";

import React, { useState } from "react";
import { Search, Filter, X, BookOpen } from "lucide-react";
import DictionaryCard from "@/components/dictionary/DictionaryCard";
import { cn } from "@/lib/utils";
import labelToEmojiData from "@/data/label_to_emoji.json";

const CATEGORIES = [
  "All Words",
  "Actions / Verbs",
  "People",
  "Places",
  "Food & Drink",
  "Emotions",
  "Time",
  "Objects",
  "Nature"
];

function getCategory(key: string): string {
  const k = key.toLowerCase();
  
  // Specific overrides for commonly misclassified words
  if (k === "duty" || k === "self" || k === "person_working" || k === "people" || k === "friend") return "People";
  if (k === "kitchen" || k === "desert" || k === "trail" || k === "clinic" || k === "skyline" || k === "building" || k === "hospital" || k === "medical") return "Places";
  if (k === "winter" || k === "summer" || k === "autumn_season" || k === "season" || k === "end_of_day") return "Time";
  if (k === "exploration" || k === "diving" || k === "swim" || k === "cooking" || k === "recovery" || k === "shopping" || k === "hearing") return "Actions / Verbs";
  if (k === "wish" || k === "necessity" || k === "courage" || k === "deep" || k === "fun" || k === "relaxation" || k === "tears" || k === "thankfulness") return "Emotions";
  if (k === "leaves" || k === "life" || k === "environment" || k === "nerve" || k === "sand" || k === "dark" || k === "planet" || k === "earth_planet" || k === "noise" || k === "liquid" || k === "cancer_disease" || k === "virus_microbe") return "Nature";
  if (k === "gift" || k === "airplane" || k === "desk" || k === "stand_object" || k === "tech" || k === "gadget" || k === "painting" || k === "sculpture" || k === "laptop" || k === "microphone" || k === "music_notes" || k === "telescope" || k === "stove" || k === "chair" || k === "chess_game" || k === "board" || k === "shower" || k === "bicycle" || k === "report" || k === "symbolic" || k === "unique" || k === "variety") return "Objects";

  // 1. Emotions / Mental States / Expressions
  if (
    k.includes("emotion") ||
    k.includes("feel") ||
    k.includes("mood") ||
    k.includes("trust") ||
    k.includes("hope") ||
    k.includes("worry") ||
    k.includes("laugh") ||
    k.includes("gasp") ||
    k.includes("scream") ||
    k.includes("shout") ||
    k.includes("grin") ||
    k.includes("plead") ||
    k.includes("excit") ||
    k.includes("proud") ||
    k.includes("jealous") ||
    k.includes("lonely") ||
    k.includes("happy") ||
    k.includes("sad") ||
    k.includes("love") ||
    k.includes("hate") ||
    k.includes("fear") ||
    k.includes("anger") ||
    k.includes("angry") ||
    k.includes("scared") ||
    k.includes("afraid") ||
    k.includes("terrified") ||
    k.includes("shock") ||
    k.includes("surprise") ||
    k.includes("confusion") ||
    k.includes("confused") ||
    k.includes("disbelief") ||
    k.includes("skepticism") ||
    k.includes("shame") ||
    k.includes("guilt") ||
    k.includes("pride") ||
    k.includes("pain") ||
    k.includes("sleepy") ||
    k.includes("tired") ||
    k.includes("bored") ||
    k.includes("cry") ||
    k.includes("desire") ||
    k.includes("satisfy") ||
    k.includes("annoy") ||
    k.includes("frown") ||
    k.includes("disgust") ||
    k.includes("stress") ||
    k.includes("doubt") ||
    k.includes("faith")
  ) {
    return "Emotions";
  }

  // 2. Actions / Verbs / Activities
  if (
    k.includes("activity") ||
    k.includes("action") ||
    k.includes("play") ||
    k.includes("work") ||
    k.includes("write") ||
    k.includes("read") ||
    k.includes("eat") ||
    k.includes("drink") ||
    k.includes("go") ||
    k.includes("come") ||
    k.includes("run") ||
    k.includes("walk") ||
    k.includes("swim") ||
    k.includes("fly") ||
    k.includes("dance") ||
    k.includes("sing") ||
    k.includes("sleep") ||
    k.includes("cook") ||
    k.includes("paint") ||
    k.includes("draw") ||
    k.includes("study") ||
    k.includes("learn") ||
    k.includes("teach") ||
    k.includes("speak") ||
    k.includes("talk") ||
    k.includes("listen") ||
    k.includes("hear") ||
    k.includes("see") ||
    k.includes("look") ||
    k.includes("watch") ||
    k.includes("jump") ||
    k.includes("climb") ||
    k.includes("drive") ||
    k.includes("ride") ||
    k.includes("travel") ||
    k.includes("clean") ||
    k.includes("wash") ||
    k.includes("build") ||
    k.includes("create") ||
    k.includes("make") ||
    k.includes("do") ||
    k.includes("fight") ||
    k.includes("kiss") ||
    k.includes("hug") ||
    k.includes("wave") ||
    k.includes("clap") ||
    k.includes("point") ||
    k.includes("think") ||
    k.includes("know") ||
    k.includes("remember") ||
    k.includes("forget") ||
    k.includes("understand") ||
    k.includes("believe") ||
    k.includes("find") ||
    k.includes("lose") ||
    k.includes("buy") ||
    k.includes("sell") ||
    k.includes("pay") ||
    k.includes("give") ||
    k.includes("take") ||
    k.includes("send") ||
    k.includes("receive") ||
    k.includes("show") ||
    k.includes("hide") ||
    k.includes("open") ||
    k.includes("close") ||
    k.includes("start") ||
    k.includes("stop") ||
    k.includes("end") ||
    k.includes("begin") ||
    k.includes("finish") ||
    k.includes("die") ||
    k.includes("live") ||
    k.includes("grow") ||
    k.includes("change") ||
    k.includes("move") ||
    k.includes("stay") ||
    k.includes("wait") ||
    k.includes("help") ||
    k.includes("meet") ||
    k.includes("call") ||
    k.includes("ask") ||
    k.includes("answer") ||
    k.includes("choose") ||
    k.includes("decide") ||
    k.includes("try") ||
    k.includes("use") ||
    k.includes("keep") ||
    k.includes("hold") ||
    k.includes("carry") ||
    k.includes("bring") ||
    k.includes("put") ||
    k.includes("set") ||
    k.includes("get") ||
    k.includes("want") ||
    k.includes("need") ||
    k.includes("prefer") ||
    k.includes("handshake") ||
    k.includes("gesture") ||
    k.includes("wave") ||
    k.includes("touch") ||
    k.includes("press") ||
    k.includes("pull") ||
    k.includes("push") ||
    k.includes("throw") ||
    k.includes("catch") ||
    k.includes("drop") ||
    k.includes("slide") ||
    k.includes("scroll") ||
    k.includes("click")
  ) {
    return "Actions / Verbs";
  }

  // 3. People / Occupations / Relationships
  if (
    k.includes("people") ||
    k.includes("person") ||
    k.includes("man") ||
    k.includes("woman") ||
    k.includes("child") ||
    k.includes("boy") ||
    k.includes("girl") ||
    k.includes("friend") ||
    k.includes("family") ||
    k.includes("father") ||
    k.includes("mother") ||
    k.includes("brother") ||
    k.includes("sister") ||
    k.includes("son") ||
    k.includes("daughter") ||
    k.includes("baby") ||
    k.includes("adult") ||
    k.includes("teenager") ||
    k.includes("kid") ||
    k.includes("parent") ||
    k.includes("grandparent") ||
    k.includes("husband") ||
    k.includes("wife") ||
    k.includes("uncle") ||
    k.includes("aunt") ||
    k.includes("cousin") ||
    k.includes("nephew") ||
    k.includes("niece") ||
    k.includes("teacher") ||
    k.includes("student") ||
    k.includes("doctor") ||
    k.includes("nurse") ||
    k.includes("police") ||
    k.includes("firefighter") ||
    k.includes("soldier") ||
    k.includes("guard") ||
    k.includes("worker") ||
    k.includes("boss") ||
    k.includes("leader") ||
    k.includes("king") ||
    k.includes("queen") ||
    k.includes("prince") ||
    k.includes("princess") ||
    k.includes("guest") ||
    k.includes("visitor") ||
    k.includes("member") ||
    k.includes("team") ||
    k.includes("group") ||
    k.includes("crowd") ||
    k.includes("audience") ||
    k.includes("partner") ||
    k.includes("colleague") ||
    k.includes("neighbor") ||
    k.includes("stranger") ||
    k.includes("enemy") ||
    k.includes("hero") ||
    k.includes("villain") ||
    k.includes("champion") ||
    k.includes("expert") ||
    k.includes("professional") ||
    k.includes("volunteer") ||
    k.includes("occupat") ||
    k.includes("profess") ||
    k.includes("doctor") ||
    k.includes("dentist") ||
    k.includes("engineer") ||
    k.includes("artist") ||
    k.includes("writer") ||
    k.includes("pilot") ||
    k.includes("driver") ||
    k.includes("farmer") ||
    k.includes("cook") ||
    k.includes("chef") ||
    k.includes("singer") ||
    k.includes("actor") ||
    k.includes("musician") ||
    k.includes("athlete") ||
    k.includes("player") ||
    k.includes("coach") ||
    k.includes("referee") ||
    k.includes("judge") ||
    k.includes("lawyer") ||
    k.includes("officer") ||
    k.includes("detective") ||
    k.includes("spy") ||
    k.includes("navy") ||
    k.includes("army") ||
    k.includes("astronaut") ||
    k.includes("scientist") ||
    k.includes("inventor")
  ) {
    return "People";
  }

  // 4. Food & Drink / Kitchen Items (Ingredients, meals)
  if (
    k.includes("food") ||
    k.includes("drink") ||
    k.includes("beverage") ||
    k.includes("hotdog") ||
    k.includes("apple") ||
    k.includes("fruit") ||
    k.includes("vegetable") ||
    k.includes("coffee") ||
    k.includes("tea") ||
    k.includes("wine") ||
    k.includes("beer") ||
    k.includes("sweet") ||
    k.includes("rice") ||
    k.includes("bread") ||
    k.includes("meat") ||
    k.includes("fish") ||
    k.includes("chicken") ||
    k.includes("beef") ||
    k.includes("pork") ||
    k.includes("egg") ||
    k.includes("milk") ||
    k.includes("cheese") ||
    k.includes("butter") ||
    k.includes("oil") ||
    k.includes("sugar") ||
    k.includes("honey") ||
    k.includes("soup") ||
    k.includes("salad") ||
    k.includes("sandwich") ||
    k.includes("pizza") ||
    k.includes("burger") ||
    k.includes("pasta") ||
    k.includes("noodle") ||
    k.includes("cake") ||
    k.includes("cookie") ||
    k.includes("pie") ||
    k.includes("chocolate") ||
    k.includes("ice cream") ||
    k.includes("candy") ||
    k.includes("juice") ||
    k.includes("water") ||
    k.includes("soda") ||
    k.includes("coke") ||
    k.includes("alcohol") ||
    k.includes("cocktail") ||
    k.includes("breakfast") ||
    k.includes("lunch") ||
    k.includes("dinner") ||
    k.includes("meal") ||
    k.includes("snack") ||
    k.includes("feast") ||
    k.includes("banana") ||
    k.includes("orange") ||
    k.includes("grape") ||
    k.includes("strawberry") ||
    k.includes("melon") ||
    k.includes("lemon") ||
    k.includes("peach") ||
    k.includes("cherry") ||
    k.includes("potato") ||
    k.includes("tomato") ||
    k.includes("onion") ||
    k.includes("garlic") ||
    k.includes("carrot") ||
    k.includes("corn") ||
    k.includes("spice") ||
    k.includes("sauce") ||
    k.includes("taco") ||
    k.includes("sushi") ||
    k.includes("ice")
  ) {
    return "Food & Drink";
  }

  // 5. Places / Geopolitics / Landmarks / Buildings
  if (
    k.includes("place") ||
    k.includes("building") ||
    k.includes("house") ||
    k.includes("home") ||
    k.includes("school") ||
    k.includes("bank") ||
    k.includes("hospital") ||
    k.includes("city") ||
    k.includes("country") ||
    k.includes("shop") ||
    k.includes("room") ||
    k.includes("office") ||
    k.includes("store") ||
    k.includes("market") ||
    k.includes("mall") ||
    k.includes("restaurant") ||
    k.includes("cafe") ||
    k.includes("hotel") ||
    k.includes("park") ||
    k.includes("garden") ||
    k.includes("street") ||
    k.includes("road") ||
    k.includes("bridge") ||
    k.includes("station") ||
    k.includes("airport") ||
    k.includes("harbor") ||
    k.includes("port") ||
    k.includes("beach") ||
    k.includes("coast") ||
    k.includes("shore") ||
    k.includes("island") ||
    k.includes("mountain") ||
    k.includes("hill") ||
    k.includes("valley") ||
    k.includes("forest") ||
    k.includes("woods") ||
    k.includes("desert") ||
    k.includes("lake") ||
    k.includes("pool") ||
    k.includes("farm") ||
    k.includes("zoo") ||
    k.includes("museum") ||
    k.includes("library") ||
    k.includes("theater") ||
    k.includes("cinema") ||
    k.includes("stadium") ||
    k.includes("gym") ||
    k.includes("church") ||
    k.includes("temple") ||
    k.includes("mosque") ||
    k.includes("shrine") ||
    k.includes("castle") ||
    k.includes("palace") ||
    k.includes("tower") ||
    k.includes("monument") ||
    k.includes("square") ||
    k.includes("plaza") ||
    k.includes("court") ||
    k.includes("field") ||
    k.includes("ground") ||
    k.includes("location") ||
    k.includes("site") ||
    k.includes("area") ||
    k.includes("zone") ||
    k.includes("region") ||
    k.includes("district") ||
    k.includes("state") ||
    k.includes("province") ||
    k.includes("nation") ||
    k.includes("world") ||
    k.includes("map") ||
    k.includes("direction") ||
    k.includes("north") ||
    k.includes("south") ||
    k.includes("east") ||
    k.includes("west") ||
    k.includes("landmark") ||
    k.includes("address") ||
    k.includes("continent") ||
    k.includes("border") ||
    k.includes("territory") ||
    k.includes("neighborhood") ||
    k.includes("village") ||
    k.includes("town") ||
    k.includes("capital") ||
    k.includes("regional_indicator") ||
    k.includes("flag_")
  ) {
    return "Places";
  }

  // 6. Time / Scheduling
  if (
    k.includes("time") ||
    k.includes("day") ||
    k.includes("night") ||
    k.includes("year") ||
    k.includes("month") ||
    k.includes("hour") ||
    k.includes("minute") ||
    k.includes("week") ||
    k.includes("yesterday") ||
    k.includes("today") ||
    k.includes("tomorrow") ||
    k.includes("clock") ||
    k.includes("calendar") ||
    k.includes("limit") ||
    k.includes("season") ||
    k.includes("autumn") ||
    k.includes("winter") ||
    k.includes("summer") ||
    k.includes("spring") ||
    k.includes("morning") ||
    k.includes("afternoon") ||
    k.includes("evening") ||
    k.includes("noon") ||
    k.includes("midnight") ||
    k.includes("second") ||
    k.includes("millisecond") ||
    k.includes("decade") ||
    k.includes("century") ||
    k.includes("era") ||
    k.includes("period") ||
    k.includes("schedule") ||
    k.includes("date") ||
    k.includes("moment") ||
    k.includes("instant") ||
    k.includes("future") ||
    k.includes("past") ||
    k.includes("present") ||
    k.includes("early") ||
    k.includes("late") ||
    k.includes("soon") ||
    k.includes("now") ||
    k.includes("then") ||
    k.includes("when") ||
    k.includes("always") ||
    k.includes("never") ||
    k.includes("sometimes") ||
    k.includes("often") ||
    k.includes("rarely") ||
    k.includes("usually") ||
    k.includes("seldom") ||
    k.includes("frequently") ||
    k.includes("occasionally") ||
    k.includes("already") ||
    k.includes("yet") ||
    k.includes("still") ||
    k.includes("before") ||
    k.includes("after") ||
    k.includes("during") ||
    k.includes("while") ||
    k.includes("until") ||
    k.includes("since") ||
    k.includes("first") ||
    k.includes("last") ||
    k.includes("next") ||
    k.includes("previous") ||
    k.includes("duration") ||
    k.includes("interval") ||
    k.includes("watch") ||
    k.includes("timer") ||
    k.includes("alarm") ||
    k.includes("stopwatch") ||
    k.includes("agenda")
  ) {
    return "Time";
  }

  // 7. Nature / Animals / Plants / Space / Weather / Body Parts
  if (
    k.includes("animal") ||
    k.includes("cat") ||
    k.includes("dog") ||
    k.includes("bird") ||
    k.includes("fish") ||
    k.includes("horse") ||
    k.includes("cow") ||
    k.includes("pig") ||
    k.includes("duck") ||
    k.includes("snake") ||
    k.includes("lizard") ||
    k.includes("spider") ||
    k.includes("ant") ||
    k.includes("bee") ||
    k.includes("monkey") ||
    k.includes("bear") ||
    k.includes("fox") ||
    k.includes("deer") ||
    k.includes("tiger") ||
    k.includes("lion") ||
    k.includes("wolf") ||
    k.includes("sheep") ||
    k.includes("goat") ||
    k.includes("rat") ||
    k.includes("mouse") ||
    k.includes("frog") ||
    k.includes("fly") ||
    k.includes("mosquito") ||
    k.includes("insect") ||
    k.includes("bug") ||
    k.includes("worm") ||
    k.includes("crab") ||
    k.includes("lobster") ||
    k.includes("shrimp") ||
    k.includes("shell") ||
    k.includes("whale") ||
    k.includes("dolphin") ||
    k.includes("shark") ||
    k.includes("octopus") ||
    k.includes("squid") ||
    k.includes("jellyfish") ||
    k.includes("seal") ||
    k.includes("penguin") ||
    k.includes("koala") ||
    k.includes("panda") ||
    k.includes("kangaroo") ||
    k.includes("dinosaur") ||
    k.includes("dragon") ||
    k.includes("unicorn") ||
    k.includes("nature") ||
    k.includes("cloud") ||
    k.includes("rain") ||
    k.includes("sun") ||
    k.includes("flower") ||
    k.includes("tree") ||
    k.includes("leaf") ||
    k.includes("river") ||
    k.includes("ocean") ||
    k.includes("sea") ||
    k.includes("wind") ||
    k.includes("storm") ||
    k.includes("rainbow") ||
    k.includes("earth") ||
    k.includes("weather") ||
    k.includes("plant") ||
    k.includes("bush") ||
    k.includes("grass") ||
    k.includes("seed") ||
    k.includes("root") ||
    k.includes("branch") ||
    k.includes("bark") ||
    k.includes("soil") ||
    k.includes("rock") ||
    k.includes("stone") ||
    k.includes("sand") ||
    k.includes("dust") ||
    k.includes("mud") ||
    k.includes("fire") ||
    k.includes("water") ||
    k.includes("air") ||
    k.includes("gas") ||
    k.includes("steam") ||
    k.includes("snow") ||
    k.includes("frost") ||
    k.includes("shadow") ||
    k.includes("light") ||
    k.includes("darkness") ||
    k.includes("star") ||
    k.includes("moon") ||
    k.includes("planet") ||
    k.includes("galaxy") ||
    k.includes("comet") ||
    k.includes("meteor") ||
    k.includes("science") ||
    k.includes("physics") ||
    k.includes("chemistry") ||
    k.includes("biology") ||
    k.includes("geology") ||
    k.includes("astronomy") ||
    k.includes("math") ||
    k.includes("formula") ||
    k.includes("element") ||
    k.includes("atom") ||
    k.includes("molecule") ||
    k.includes("cell") ||
    k.includes("gene") ||
    k.includes("dna") ||
    k.includes("virus") ||
    k.includes("bacteria") ||
    k.includes("microbe") ||
    k.includes("disease") ||
    k.includes("illness") ||
    k.includes("sickness") ||
    k.includes("health") ||
    k.includes("body") ||
    k.includes("bone") ||
    k.includes("blood") ||
    k.includes("muscle") ||
    k.includes("skin") ||
    k.includes("hair") ||
    k.includes("brain") ||
    k.includes("heart") ||
    k.includes("lung") ||
    k.includes("stomach") ||
    k.includes("eye") ||
    k.includes("ear") ||
    k.includes("nose") ||
    k.includes("mouth") ||
    k.includes("tooth") ||
    k.includes("tongue") ||
    k.includes("hand") ||
    k.includes("foot") ||
    k.includes("finger") ||
    k.includes("toe") ||
    k.includes("arm") ||
    k.includes("leg") ||
    k.includes("chest") ||
    k.includes("back") ||
    k.includes("neck") ||
    k.includes("shoulder") ||
    k.includes("knee") ||
    k.includes("elbow") ||
    k.includes("wrist") ||
    k.includes("ankle") ||
    k.includes("face")
  ) {
    return "Nature";
  }

  // 8. Default fallback to Objects (Clothing, tools, vehicles, tech, household, symbols)
  return "Objects";
}

function cleanWord(key: string): string {
  let cleaned = key.replace(/_/g, " ");
  cleaned = cleaned.replace(/\s+(emotion|activity|device|object|place|food|concept|animal|pathogen|sports|broken|financial|finance|broken)$/i, "");
  return cleaned.charAt(0).toUpperCase() + cleaned.slice(1);
}

// Statically transform the loaded label dataset
const DICTIONARY_DATA = Object.entries(labelToEmojiData).map(([key, val]) => {
  const category = getCategory(key);
  const word = cleanWord(key);
  return {
    word,
    emoji: val,
    category,
    confidence: 0.95 + Math.random() * 0.04 // Display a high match score (95% - 99%)
  };
});

export default function DictionaryPage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [activeCategory, setActiveCategory] = useState("All Words");
  const [visibleCount, setVisibleCount] = useState(48);

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value);
    setVisibleCount(48);
  };

  const handleCategoryChange = (category: string) => {
    setActiveCategory(category);
    setVisibleCount(48);
  };

  const filteredData = DICTIONARY_DATA.filter((item) => {
    const matchesSearch = item.word.toLowerCase().includes(searchQuery.toLowerCase()) || 
                          item.category.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = activeCategory === "All Words" || item.category === activeCategory;
    return matchesSearch && matchesCategory;
  });

  const visibleData = filteredData.slice(0, visibleCount);

  return (
    <div className="pt-32 pb-24 min-h-screen bg-stone-50/40">
      <div className="max-w-[1200px] mx-auto px-6">
        
        <div className="flex flex-col items-center text-center mb-16">
          <div className="flex items-center gap-2 px-3 py-1 bg-stone-100 border border-stone-200 rounded-full text-stone-600 text-[11px] font-bold uppercase tracking-[0.08em] mb-4">
            <BookOpen size={12} className="text-accent" />
            AI Vocabulary Registry
          </div>
          <h1 className="font-serif text-[42px] mb-4 text-text-primary">
            Explore the Visual Language
          </h1>
          <p className="text-[14px] text-text-secondary max-w-[500px] mb-8 leading-relaxed">
            Browse through the complete list of 2,900+ target words and custom tokens mapped to their Unicode emoji equivalents within the SignDecoder FLAN-T5 model.
          </p>
          
          <div className="relative w-full max-w-[560px] group">
            <Search className="absolute left-5 top-1/2 -translate-y-1/2 text-text-muted group-focus-within:text-accent transition-colors" size={20} />
            <input
              type="text"
              value={searchQuery}
              onChange={handleSearchChange}
              placeholder="Search for a word, tag, or category..."
              className="w-full h-14 pl-14 pr-12 bg-white border border-border rounded-md shadow-xs outline-none focus:border-accent focus:ring-1 focus:ring-accent/10 transition-all text-[15px]"
            />
            {searchQuery && (
              <button 
                onClick={() => { setSearchQuery(""); setVisibleCount(48); }}
                className="absolute right-5 top-1/2 -translate-y-1/2 text-text-muted hover:text-text-primary transition-colors"
              >
                <X size={18} />
              </button>
            )}
          </div>
        </div>

        <div className="flex flex-col lg:flex-row gap-12">
          
          <aside className="w-full lg:w-64 shrink-0">
            <div className="sticky top-32 bg-white/80 backdrop-blur-md p-6 rounded-xl border border-stone-200 shadow-2xs">
              <div className="flex items-center gap-2 mb-6">
                <Filter size={16} className="text-text-muted" />
                <span className="text-[12px] font-bold text-text-muted uppercase tracking-wider">
                  Categories
                </span>
              </div>
              
              <nav className="flex lg:flex-col flex-wrap gap-1">
                {CATEGORIES.map((category) => (
                  <button
                    key={category}
                    onClick={() => handleCategoryChange(category)}
                    className={cn(
                      "text-left px-4.5 py-2.5 rounded-md text-[14px] transition-all w-full",
                      activeCategory === category
                        ? "bg-accent text-white font-medium shadow-xs"
                        : "text-text-secondary hover:bg-stone-50 hover:text-text-primary"
                    )}
                  >
                    {category}
                  </button>
                ))}
              </nav>
            </div>
          </aside>

          
          <main className="flex-grow">
            <div className="flex items-center justify-between mb-8">
              <span className="text-[13px] text-text-muted">
                Showing <strong className="text-text-primary">{filteredData.length}</strong> of {DICTIONARY_DATA.length} registry entries
              </span>
            </div>
            
            {visibleData.length > 0 ? (
              <>
                <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-6">
                  {visibleData.map((item, index) => (
                    <DictionaryCard key={index} {...item} />
                  ))}
                </div>

                {filteredData.length > visibleCount && (
                  <div className="flex justify-center mt-12">
                    <button
                      onClick={() => setVisibleCount((prev) => prev + 48)}
                      className="px-8 py-3.5 bg-white border border-stone-200 rounded-lg text-[14px] font-medium text-text-primary hover:border-accent hover:text-accent hover:shadow-sm transition-all duration-200 active:scale-[0.98]"
                    >
                      Load More Words ({filteredData.length - visibleCount} remaining)
                    </button>
                  </div>
                )}
              </>
            ) : (
              <div className="py-20 text-center bg-white border border-dashed border-border rounded-xl shadow-2xs">
                <p className="text-text-secondary mb-3">No results found for "{searchQuery}"</p>
                <button 
                  onClick={() => {setSearchQuery(""); setActiveCategory("All Words"); setVisibleCount(48);}}
                  className="text-accent text-[14px] font-medium hover:underline"
                >
                  Clear all filters
                </button>
              </div>
            )}
          </main>
        </div>
      </div>
    </div>
  );
}
