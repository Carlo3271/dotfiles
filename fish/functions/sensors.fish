function sensors --wraps sensors --description 'Show compact CPU and GPU temperatures by default'
    if test (count $argv) -gt 0
        command sensors $argv
        return
    end

    temps
end
