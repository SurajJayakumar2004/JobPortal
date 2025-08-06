package com.appdeduplicator;

import org.json.JSONObject;
import java.io.*;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.*;

public class ConfigManager {
    private Properties config;
    private JSONObject rules;
    private static final String CONFIG_FILE = "config.properties";
    private static final String DEFAULT_RULES_FILE = "rules.json";

    public ConfigManager() throws IOException {
        loadConfig();
        loadRules();
    }

    private void loadConfig() throws IOException {
        config = new Properties();
        File configFile = new File(CONFIG_FILE);
        
        if (!configFile.exists()) {
            createDefaultConfig();
        }
        
        try (FileInputStream fis = new FileInputStream(configFile)) {
            config.load(fis);
        }
    }

    private void createDefaultConfig() throws IOException {
        Properties defaultConfig = new Properties();
        defaultConfig.setProperty("scan.directory", "./test-apps");
        defaultConfig.setProperty("rules.file", DEFAULT_RULES_FILE);
        
        try (FileOutputStream fos = new FileOutputStream(CONFIG_FILE)) {
            defaultConfig.store(fos, "AppDeduplicator Configuration");
        }
        
        config = defaultConfig;
        System.out.println("Created default config.properties file");
    }

    private void loadRules() throws IOException {
        String rulesFile = config.getProperty("rules.file", DEFAULT_RULES_FILE);
        File file = new File(rulesFile);
        
        if (!file.exists()) {
            createDefaultRules(rulesFile);
        }
        
        String content = new String(Files.readAllBytes(Paths.get(rulesFile)));
        rules = new JSONObject(content);
    }

    private void createDefaultRules(String rulesFile) throws IOException {
        JSONObject defaultRules = new JSONObject();
        defaultRules.put("Browser", Arrays.asList("chrome", "firefox", "edge", "safari", "opera"));
        defaultRules.put("Media", Arrays.asList("vlc", "spotify", "netflix", "media", "player", "music"));
        defaultRules.put("IDE", Arrays.asList("vscode", "intellij", "eclipse", "netbeans", "code", "studio"));
        defaultRules.put("Office", Arrays.asList("word", "excel", "powerpoint", "office", "writer", "calc"));
        defaultRules.put("Games", Arrays.asList("game", "steam", "epic", "origin", "uplay"));
        defaultRules.put("System", Arrays.asList("system", "driver", "update", "antivirus", "security"));
        
        try (FileWriter writer = new FileWriter(rulesFile)) {
            writer.write(defaultRules.toString(2));
        }
        
        System.out.println("Created default " + rulesFile + " file");
    }

    public String getScanDirectory() {
        return config.getProperty("scan.directory", "./test-apps");
    }

    public String getRulesFile() {
        return config.getProperty("rules.file", DEFAULT_RULES_FILE);
    }

    public JSONObject getRules() {
        return rules;
    }

    public Set<String> getCategories() {
        return rules.keySet();
    }

    public List<String> getKeywordsForCategory(String category) {
        if (rules.has(category)) {
            return rules.getJSONArray(category).toList().stream()
                    .map(Object::toString)
                    .collect(ArrayList::new, ArrayList::add, ArrayList::addAll);
        }
        return new ArrayList<>();
    }
}