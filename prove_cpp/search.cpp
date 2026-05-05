#include "search.h"
#include <vector>
#include <string>
#include <cstdlib>
#include <cstdio>
#include <cctype>

std::string url_encode(const std::string &value) {
    std::string escaped;
    for (char c : value) {
        if (isalnum(static_cast<unsigned char>(c)) || c == '-' || c == '_' || c == '.' || c == '~') {
            escaped += c;
        } else if (c == ' ') {
            escaped += '+';
        } else {
            char buf[4];
            snprintf(buf, sizeof(buf), "%%%02X", static_cast<unsigned char>(c));
            escaped += buf;
        }
    }
    return escaped;
}

void execute_search(const std::string& sanitized_user_input) {
    std::vector<std::string> ops = {
        "verafiles.org", "rappler.com", "tsek.ph", "mindanews.com",
        "pressone.ph", "news.abs-cbn.com", "philstar.com"
    };
    
    std::string op_parts;
    for (size_t i = 0; i < ops.size(); ++i) {
        op_parts += "site:" + ops[i];
        if (i < ops.size() - 1) op_parts += " OR ";
    }
    
    std::string user_part = sanitized_user_input;
    user_part.erase(0, user_part.find_first_not_of(" \t\r\n"));
    user_part.erase(user_part.find_last_not_of(" \t\r\n") + 1);

    std::string final_query = "(" + op_parts + ") " + user_part;
    std::string url = "https://www.google.com/search?q=" + url_encode(final_query);
    
#if defined(_WIN32)
    std::string cmd = "start \"\" \"" + url + "\"";
#elif defined(__APPLE__)
    std::string cmd = "open \"" + url + "\"";
#else
    std::string cmd = "xdg-open \"" + url + "\"";
#endif

    std::system(cmd.c_str());
}
