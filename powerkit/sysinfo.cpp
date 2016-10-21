/*
 * Copyright (C) 2016 xizhouf
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */
#include <iostream>
#include <cstdlib>
#include "msr_reader.h"
using namespace std;

int main(int argc, char *argv[]) {

    if (argc > 1) {
        for (int i = 1; i < argc; i++) {
            int coreID = atoi(argv[i]);
            MSRReader msr(coreID);
            PowerInfo pkgPowerInfo, dramPowerInfo;

            msr.getPkgPowerInfor(pkgPowerInfo);
            msr.getDramPowerInfor(dramPowerInfo);

            cout << "PKG_POWER_INFO: " << pkgPowerInfo.minPower << ' ' << pkgPowerInfo.maxPower << ' ' << pkgPowerInfo.thermalSpecPower << endl;
            cout << "DRAM_POWER_INFO: " << dramPowerInfo.minPower << ' ' << dramPowerInfo.maxPower << ' ' << dramPowerInfo.thermalSpecPower << endl;
        }
    }
}
