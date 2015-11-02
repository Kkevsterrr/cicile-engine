require 'net/http'
require 'cgi'
require 'csv'
require 'colorize'

def download(id)
    #    url = URI.parse("http://en.lichess.org/training/#{id}")
    url = URI.parse("http://chess.emrald.net/psolution.php?Pos=#{id}")
    req = Net::HTTP::Get.new(url.to_s)
    # cookie1 = CGI::Cookie.new('sessionId', 'Ripp103p4zC0')
    #req['Cookie'] = cookie1.to_s
    res = Net::HTTP.start(url.host, url.port) {|http|
        http.request(req)
    }
    return res.body
end
total = 65500
print "Downloading..."
CSV.open("tactics2", "w") do |csv|
    for i in 45820..total do
        a = Array.new()
        a << i
        page = download(i)
        print "\rDownloading...#{i}/#{total}"
        page.split(/\n/).each { |line|
            p page
            if line.include?("Boards[") #&& !line.include?("<")
                a << line.split(/"/)[1]
            end
        }
        csv << a
        #p csv
        #sleep(0.01)
    end
end
print "\rDownloading..."
puts "done".green
