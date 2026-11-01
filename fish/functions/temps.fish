function temps --description 'Show one CPU temperature and one GPU temperature'
    command sensors | awk '
        /^[^[:space:]].*$/ && $0 !~ /:/ {
            chip = $1
        }

        chip ~ /^radeon-pci-/ && /^temp1:/ && gpu == "" {
            gpu = $2
            sub(/^\+/, "", gpu)
        }

        chip ~ /^coretemp-/ && /^Package id 0:/ {
            cpu = $4
            sub(/^\+/, "", cpu)
        }

        END {
            print "CPU " (cpu != "" ? cpu : "N/A")
            print "GPU " (gpu != "" ? gpu : "N/A")
        }
    '
end
