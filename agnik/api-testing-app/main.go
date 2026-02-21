package main

import (
	"crypto/tls"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"strings"
	"time"

	"gopkg.in/yaml.v3"
)

// ANSI colors
const (
	Reset  = "\033[0m"
	Red    = "\033[31m"
	Green  = "\033[32m"
	Yellow = "\033[33m"
	Cyan   = "\033[36m"
	Bold   = "\033[1m"
)

type Config struct {
	Smo struct {
		Host           string `yaml:"host"`
		A1pmsPort      int    `yaml:"a1pms_port"`
		InfluxdbPort   int    `yaml:"influxdb_port"`
		InfluxdbToken  string `yaml:"influxdb_token"`
		InfluxdbOrg    string `yaml:"influxdb_org"`
		InfluxdbBucket string `yaml:"influxdb_bucket"`
		KafkaAdminPort int    `yaml:"kafka_admin_port"`
		SdnrPort       int    `yaml:"sdnr_port"`
		SdnrUser       string `yaml:"sdnr_user"`
		SdnrPassword   string `yaml:"sdnr_password"`
	} `yaml:"smo"`
	Ric struct {
		Host           string `yaml:"host"`
		A1MediatorPort int    `yaml:"a1_mediator_port"`
		E2mgrPort      int    `yaml:"e2mgr_port"`
		AppmgrPort     int    `yaml:"appmgr_port"`
		RtmgrPort      int    `yaml:"rtmgr_port"`
	} `yaml:"ric"`
}

var client = &http.Client{
	Timeout: 5 * time.Second,
	Transport: &http.Transport{
		TLSClientConfig: &tls.Config{InsecureSkipVerify: true},
	},
}

func main() {
	fmt.Printf("\n%s============================================================%s\n", Bold, Reset)
	fmt.Printf("%s  O-RAN SYSTEM HEALTH CHECK (Golang)%s\n", Bold, Reset)
	fmt.Printf("%s============================================================%s\n", Bold, Reset)

	data, err := os.ReadFile("config.yaml")
	if err != nil {
		fmt.Printf("%sERROR: Cannot open config.yaml: %v%s\n", Red, err, Reset)
		os.Exit(1)
	}

	var cfg Config
	if err := yaml.Unmarshal(data, &cfg); err != nil {
		fmt.Printf("%sERROR: Cannot parse config.yaml: %v%s\n", Red, err, Reset)
		os.Exit(1)
	}

	fmt.Printf("  SMO  : %s\n", cfg.Smo.Host)
	fmt.Printf("  RIC  : %s\n", cfg.Ric.Host)
	fmt.Printf("  Time : %s\n", time.Now().Format("2006-01-02 15:04:05"))
	fmt.Printf("%s============================================================%s\n\n", Bold, Reset)

	results := make(map[string]interface{})

	checkKafka(&cfg, results)
	checkGNBs(&cfg, results)
	checkPolicies(&cfg, results)
	checkMetrics(&cfg, results)
	checkInterfaces(&cfg, results)

	fmt.Printf("\n%s============================================================%s\n", Bold, Reset)
	fmt.Printf("%s  SUMMARY%s\n", Bold, Reset)
	fmt.Printf("%s============================================================%s\n", Bold, Reset)
	fmt.Printf("  %-45s %v\n", "Kafka topics:", results["kafka_topics"])
	fmt.Printf("  %-45s %v\n", "gNBs (E2Mgr):", results["e2mgr_gnbs"])
	fmt.Printf("  %-45s %v\n", "gNBs (OAM/SDNC):", results["oam_gnbs"])
	fmt.Printf("  %-45s %v\n", "Active A1 Policies:", results["policies"])
	fmt.Printf("  %-45s %v / %v\n", "Interfaces passed:", results["iface_passed"], results["iface_total"])
	fmt.Println()
}

func section(title string) {
	fmt.Printf("\n%s%s════════════════════════════════════════════════════════════%s\n", Bold, Cyan, Reset)
	fmt.Printf("%s%s  %s%s\n", Bold, Cyan, title, Reset)
	fmt.Printf("%s%s════════════════════════════════════════════════════════════%s\n", Bold, Cyan, Reset)
}

func resultOut(label, status, detail string) {
	detailStr := ""
	if detail != "" {
		detailStr = "  → " + detail
	}
	fmt.Printf("  %-45s %s%s\n", label, status, detailStr)
}

func Pass() string { return Green + "✅ PASS" + Reset }
func Fail() string { return Red + "❌ FAIL" + Reset }
func Warn() string { return Yellow + "⚠️  WARN" + Reset }
func Info() string { return Cyan + "ℹ️  INFO" + Reset }

func getRequest(url, user, pass string) (*http.Response, []byte, error) {
	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		return nil, nil, err
	}
	if user != "" || pass != "" {
		req.SetBasicAuth(user, pass)
		req.Header.Set("Accept", "application/json")
	}
	resp, err := client.Do(req)
	if err != nil {
		return nil, nil, err
	}
	defer resp.Body.Close()
	body, _ := io.ReadAll(resp.Body)
	return resp, body, nil
}

// 1. Kafka Message Flow
func checkKafka(cfg *Config, results map[string]interface{}) {
	section("1. Message Flow — Kafka / Strimzi")
	url := fmt.Sprintf("http://%s:%d/api/topics", cfg.Smo.Host, cfg.Smo.KafkaAdminPort)
	resp, body, err := getRequest(url, "", "")
	
	results["kafka_topics"] = "?"
	
	if err != nil || resp.StatusCode != 200 {
		// Fallback check: is the port open?
		urlRoot := fmt.Sprintf("http://%s:%d", cfg.Smo.Host, cfg.Smo.KafkaAdminPort)
		respFallback, _, errFallback := getRequest(urlRoot, "", "")
		if errFallback == nil && respFallback != nil {
			resultOut("Kafka bootstrap reachable", Warn(), fmt.Sprintf("%s:%d is up but no REST admin API.", cfg.Smo.Host, cfg.Smo.KafkaAdminPort))
		} else {
			resultOut("Kafka bootstrap reachable", Fail(), fmt.Sprintf("Cannot reach %s:%d", cfg.Smo.Host, cfg.Smo.KafkaAdminPort))
		}
		return
	}

	var topicData map[string]interface{}
	if err := json.Unmarshal(body, &topicData); err == nil {
		if topicsList, ok := topicData["topics"].([]interface{}); ok {
			results["kafka_topics"] = len(topicsList)
			resultOut("Kafka topics discovered", Pass(), fmt.Sprintf("Total: %d", len(topicsList)))
		} else {
			resultOut("Kafka topic list", Warn(), "Unexpected response format")
		}
		
	} else {
		resultOut("Kafka topic list", Warn(), "Unexpected response format")
	}
}

// 2. gNB Count
func checkGNBs(cfg *Config, results map[string]interface{}) {
	section("2. gNB Count — OAM (SDNC) + Near-RT RIC (E2Mgr)")
	results["oam_gnbs"] = "?"
	results["e2mgr_gnbs"] = "?"

	// OAM PATH (SDNC)
	urlOAM := fmt.Sprintf("http://%s:%d/rests/data/network-topology:network-topology", cfg.Smo.Host, cfg.Smo.SdnrPort)
	respOAM, bodyOAM, err := getRequest(urlOAM, cfg.Smo.SdnrUser, cfg.Smo.SdnrPassword)
	if err == nil && respOAM.StatusCode == 200 {
		var data map[string]interface{}
		json.Unmarshal(bodyOAM, &data)
		connected := 0
		total := 0
		if topo, ok := data["network-topology:topology"].([]interface{}); ok && len(topo) > 0 {
			if tmap, ok := topo[0].(map[string]interface{}); ok {
				if nodes, ok := tmap["node"].([]interface{}); ok {
					total = len(nodes)
					for _, n := range nodes {
						if nmap, ok := n.(map[string]interface{}); ok {
							if status, ok := nmap["netconf-node-topology:connection-status"].(string); ok && status == "connected" {
								connected++
								fmt.Printf("    • %v\n", nmap["node-id"])
							}
						}
					}
				}
			}
		}
		results["oam_gnbs"] = connected
		if connected > 0 {
			resultOut("OAM gNBs connected (SDNC)", Pass(), fmt.Sprintf("%d connected / %d total", connected, total))
		} else {
			resultOut("OAM gNBs connected (SDNC)", Pass(), fmt.Sprintf("%d connected / %d total (OK for fresh state)", connected, total))
		}
	} else {
		code := "no response"
		if respOAM != nil {
			code = fmt.Sprintf("HTTP %d", respOAM.StatusCode)
		}
		resultOut("OAM SDNC RESTCONF", Fail(), code)
	}

	// RIC PATH (E2Mgr)
	urlE2 := fmt.Sprintf("http://%s:%d/v1/nodeb/states", cfg.Ric.Host, cfg.Ric.E2mgrPort)
	respE2, bodyE2, err := getRequest(urlE2, "", "")
	if err == nil && respE2.StatusCode == 200 {
		var nodes []map[string]interface{}
		json.Unmarshal(bodyE2, &nodes)
		connected := 0
		for _, n := range nodes {
			if n["connectionStatus"] != "DISCONNECTED" {
				connected++
				fmt.Printf("    • %v (%v)\n", n["inventoryName"], n["connectionStatus"])
			}
		}
		results["e2mgr_gnbs"] = connected
		if connected > 0 {
			resultOut("Near-RT RIC E2Mgr NodeB list", Pass(), fmt.Sprintf("%d gNBs registered", connected))
		} else {
			resultOut("Near-RT RIC E2Mgr NodeB list", Pass(), fmt.Sprintf("%d gNBs registered (OK for fresh state)", connected))
		}
	} else {
		code := "no response"
		if respE2 != nil {
			code = fmt.Sprintf("HTTP %d", respE2.StatusCode)
		}
		resultOut("Near-RT RIC E2Mgr", Fail(), code)
	}
}

// 3. Policies
func checkPolicies(cfg *Config, results map[string]interface{}) {
	section("3. Policies — A1 Mediator + A1PMS")
	results["policies"] = "?"

	urlA1pms := fmt.Sprintf("http://%s:%d/a1-policy/v2/policies", cfg.Smo.Host, cfg.Smo.A1pmsPort)
	respA1pms, bodyA1pms, err := getRequest(urlA1pms, "", "")
	if err == nil && respA1pms.StatusCode == 200 {
		var data map[string]interface{}
		json.Unmarshal(bodyA1pms, &data)
		if policyIds, ok := data["policy_ids"].([]interface{}); ok {
			results["policies"] = len(policyIds)
			resultOut("A1PMS active policies", Pass(), fmt.Sprintf("%d policies", len(policyIds)))
		}
	} else {
		code := "no response"
		if respA1pms != nil {
			code = fmt.Sprintf("HTTP %d", respA1pms.StatusCode)
		}
		resultOut("A1PMS active policies", Fail(), code)
	}

	urlA1med := fmt.Sprintf("http://%s:%d/A1-P/v2/policytypes", cfg.Ric.Host, cfg.Ric.A1MediatorPort)
	respA1med, bodyA1med, err := getRequest(urlA1med, "", "")
	if err == nil && respA1med.StatusCode == 200 {
		var types []interface{}
		json.Unmarshal(bodyA1med, &types)
		if len(types) > 0 {
			resultOut("A1 Mediator policy types", Pass(), fmt.Sprintf("%d types registered by xApps", len(types)))
		} else {
			resultOut("A1 Mediator policy types", Pass(), "0 types registered by xApps (OK for fresh state)")
		}
	} else {
		code := "no response"
		if respA1med != nil {
			code = fmt.Sprintf("HTTP %d", respA1med.StatusCode)
		}
		resultOut("A1 Mediator policy types", Fail(), code)
	}
}

// 4. Metrics
func checkMetrics(cfg *Config, results map[string]interface{}) {
	section("4. Metrics — InfluxDB")
	urlPing := fmt.Sprintf("http://%s:%d/ping", cfg.Smo.Host, cfg.Smo.InfluxdbPort)
	respPing, _, err := getRequest(urlPing, "", "")
	if err == nil && (respPing.StatusCode == 200 || respPing.StatusCode == 204) {
		resultOut("InfluxDB ping", Pass(), fmt.Sprintf("%s:%d", cfg.Smo.Host, cfg.Smo.InfluxdbPort))
	} else {
		code := "no response"
		if respPing != nil {
			code = fmt.Sprintf("HTTP %d", respPing.StatusCode)
		}
		resultOut("InfluxDB ping", Fail(), code)
		return
	}

	urlBuckets := fmt.Sprintf("http://%s:%d/api/v2/buckets?org=%s", cfg.Smo.Host, cfg.Smo.InfluxdbPort, cfg.Smo.InfluxdbOrg)
	req, _ := http.NewRequest("GET", urlBuckets, nil)
	if cfg.Smo.InfluxdbToken != "" {
		req.Header.Add("Authorization", "Token "+cfg.Smo.InfluxdbToken)
	}
	respBuckets, err := client.Do(req)
	if err == nil && respBuckets.StatusCode == 200 {
		body, _ := io.ReadAll(respBuckets.Body)
		var data map[string]interface{}
		json.Unmarshal(body, &data)
		if buckets, ok := data["buckets"].([]interface{}); ok {
			resultOut("InfluxDB buckets", Pass(), fmt.Sprintf("%d found", len(buckets)))
		}
	} else {
		code := "no response"
		if respBuckets != nil {
			code = fmt.Sprintf("HTTP %d", respBuckets.StatusCode)
		}
		resultOut("InfluxDB buckets", Info(), code)
	}

	// Just a simple query check for PM Data using Post
	urlQuery := fmt.Sprintf("http://%s:%d/api/v2/query?org=%s", cfg.Smo.Host, cfg.Smo.InfluxdbPort, cfg.Smo.InfluxdbOrg)
	fluxQuery := fmt.Sprintf("from(bucket: \"%s\") |> range(start: -1h) |> first() |> limit(n: 5)", cfg.Smo.InfluxdbBucket)
	
	reqQ, _ := http.NewRequest("POST", urlQuery, strings.NewReader(fluxQuery))
	reqQ.Header.Add("Content-Type", "application/vnd.flux")
	reqQ.Header.Add("Accept", "application/csv")
	if cfg.Smo.InfluxdbToken != "" {
		reqQ.Header.Add("Authorization", "Token "+cfg.Smo.InfluxdbToken)
	}
	
	respQ, err := client.Do(reqQ)
	if err == nil && respQ.StatusCode == 200 {
		body, _ := io.ReadAll(respQ.Body)
		lines := strings.Split(strings.TrimSpace(string(body)), "\n")
		count := 0
		for _, l := range lines {
			if l != "" && !strings.HasPrefix(l, "#") {
				count++
			}
		}
		if count > 1 {
			resultOut(fmt.Sprintf("PM data in '%s'", cfg.Smo.InfluxdbBucket), Pass(), fmt.Sprintf("%d data rows found", count-1))
		} else {
			resultOut(fmt.Sprintf("PM data in '%s'", cfg.Smo.InfluxdbBucket), Info(), "No data in last 1h")
		}
	} else {
		code := "no response"
		if respQ != nil {
			code = fmt.Sprintf("HTTP %d", respQ.StatusCode)
		}
		resultOut(fmt.Sprintf("PM data query '%s'", cfg.Smo.InfluxdbBucket), Info(), "No data / " + code)
	}
}

// 5. Interfaces
func checkInterfaces(cfg *Config, results map[string]interface{}) {
	section("5. Interface Accessibility — Health Endpoints")

	endpoints := []struct {
		label string
		url   string
		user  string
		pass  string
	}{
		{"A1 Mediator", fmt.Sprintf("http://%s:%d/A1-P/v2/healthcheck", cfg.Ric.Host, cfg.Ric.A1MediatorPort), "", ""},
		{"E2Mgr", fmt.Sprintf("http://%s:%d/v1/health", cfg.Ric.Host, cfg.Ric.E2mgrPort), "", ""},
		{"AppMgr", fmt.Sprintf("http://%s:%d/ric/v1/health/alive", cfg.Ric.Host, cfg.Ric.AppmgrPort), "", ""},
		{"RtMgr", fmt.Sprintf("http://%s:%d/ric/v1/getdebuginfo", cfg.Ric.Host, cfg.Ric.RtmgrPort), "", ""},
		{"A1PMS", fmt.Sprintf("http://%s:%d/a1-policy/v2/status", cfg.Smo.Host, cfg.Smo.A1pmsPort), "", ""},
		{"InfluxDB", fmt.Sprintf("http://%s:%d/ping", cfg.Smo.Host, cfg.Smo.InfluxdbPort), "", ""},
		{"SDNC RESTCONF", fmt.Sprintf("http://%s:%d/rests/data/network-topology:network-topology", cfg.Smo.Host, cfg.Smo.SdnrPort), cfg.Smo.SdnrUser, cfg.Smo.SdnrPassword},
	}

	passed := 0
	for _, ep := range endpoints {
		resp, _, err := getRequest(ep.url, ep.user, ep.pass)
		if err == nil && (resp.StatusCode >= 200 && resp.StatusCode < 300) {
			resultOut(ep.label, Pass(), fmt.Sprintf("HTTP %d", resp.StatusCode))
			passed++
		} else {
			code := "unreachable"
			if resp != nil {
				code = fmt.Sprintf("HTTP %d", resp.StatusCode)
			}
			resultOut(ep.label, Fail(), code)
		}
	}
	results["iface_passed"] = passed
	results["iface_total"] = len(endpoints)
}
