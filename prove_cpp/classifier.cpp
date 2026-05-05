#include "classifier.h"
#include "data_loader.h"
#include <regex>

bool host_in_set(const std::string& host, const std::unordered_set<std::string>& domains) {
    std::string h = data_loader::normalize_domain(host);
    if (h.empty()) return false;
    if (domains.find(h) != domains.end()) return true;
    for (const auto& d : domains) {
        if (!d.empty() && (h == d || (h.length() > d.length() && h.substr(h.length() - d.length() - 1) == "." + d))) {
            return true;
        }
    }
    return false;
}

std::tuple<std::string, std::string> process_input(const std::string& raw) {
    std::string s = raw;
    s.erase(0, s.find_first_not_of(" \t\r\n"));
    s.erase(s.find_last_not_of(" \t\r\n") + 1);
    if (s.empty()) return {"text", ""};

    std::regex url_scheme("^https?://", std::regex_constants::icase);
    std::regex domain_like("^([a-z0-9]([a-z0-9-]*[a-z0-9])?\\.)+[a-z]{2,}", std::regex_constants::icase);

    if (std::regex_search(s, url_scheme)) {
        std::string candidate = s;
        auto pos = candidate.find("://");
        if (pos != std::string::npos) {
            candidate = candidate.substr(pos + 3);
        }
        std::string netloc = candidate.substr(0, candidate.find_first_of("/?#"));
        if (netloc.empty() && candidate.find('/') != std::string::npos) {
            auto parts = candidate.substr(candidate.find('/') + 1);
            if (parts.find('/') != std::string::npos) {
                netloc = parts.substr(0, parts.find('/'));
            } else {
                netloc = parts;
            }
        }
        std::string domain = data_loader::normalize_domain(netloc);
        if (!domain.empty()) return {"url", domain};
        return {"text", s};
    }
    
    std::string first_token = s.substr(0, s.find_first_of(" \t"));
    std::string host_part = first_token.substr(0, first_token.find_first_of("/?#"));
    if (std::regex_search(host_part, domain_like)) {
        std::string domain = data_loader::normalize_domain(host_part);
        if (!domain.empty()) return {"url", domain};
    }

    return {"text", s};
}

std::string evaluate_credibility(const std::string& input_type, const std::string& parsed_value) {
    if (input_type != "url" || parsed_value.empty()) return "UNKNOWN";
    std::string d = data_loader::normalize_domain(parsed_value);
    if (host_in_set(d, data_loader::blocklist_set)) return "FAKE";
    if (host_in_set(d, data_loader::ugc_platforms_set)) return "UGC";
    return "UNKNOWN";
}
