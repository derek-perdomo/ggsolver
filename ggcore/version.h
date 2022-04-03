#ifndef GGCORE_VERSION_H
#define GGCORE_VERSION_H

#include <string>

#define GGCORE_VERSION_MAJOR 0
#define GGCORE_VERSION_MINOR 1
#define GGCORE_VERSION_PATCH 0


namespace ggsolver {

		inline std::string ggsolver_version() {
			return std::string(
				std::to_string(GGCORE_VERSION_MAJOR) + "." +
				std::to_string(GGCORE_VERSION_MINOR) + "." +
				std::to_string(GGCORE_VERSION_PATCH)
			);
		}

	}
#endif