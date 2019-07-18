import common
import settings


def start(directory):
    nodes = settings.getnodes('clients', 'osds', 'mons', 'rgws')
    collectl_dir = '%s/collectl' % directory
    # perf_dir = '%s/perf' % directory
    # blktrace_dir = '%s/blktrace' % directory

    # collectl
    rawdskfilt = '+cciss/c\d+d\d+ |hd[ab] | sd[a-z]+ |dm-\d+ |xvd[a-z] |fio[a-z]+ | vd[a-z]+ |emcpower[a-z]+ |psv\d+ |nvme[0-9]n[0-9]+p[0-9]+ '
    common.pdsh(nodes, 'mkdir -p -m0755 -- %s' % collectl_dir)
    #common.pdsh(nodes, 'collectl -s+mYZ -i 1:10 --rawdskfilt "%s" -F0 -f %s' % (rawdskfilt, collectl_dir))

    # perf
    # common.pdsh(nodes), 'mkdir -p -m0755 -- %s' % perf_dir).communicate()
    # common.pdsh(nodes), 'cd %s;sudo perf_3.6 record -g -f -a -F 100 -o perf.data' % perf_dir)

    # blktrace
    # common.pdsh(osds, 'mkdir -p -m0755 -- %s' % blktrace_dir).communicate()
    # for device in xrange (0,osds_per_node):
    #     common.pdsh(osds, 'cd %s;sudo blktrace -o device%s -d /dev/disk/by-partlabel/osd-device-%s-data'
    #                 % (blktrace_dir, device, device))


def stop(directory=None):
    nodes = settings.getnodes('clients', 'osds', 'mons', 'rgws')

    common.pdsh(nodes, 'killall -SIGINT -f collectl').communicate()
    common.pdsh(nodes, 'sudo pkill -SIGINT -f perf_3.6').communicate()
    common.pdsh(settings.getnodes('osds'), 'sudo pkill -SIGINT -f blktrace').communicate()
    if directory:
        sc = settings.cluster
        common.pdsh(nodes, 'sudo chown %s.%s %s/perf/perf.data' % (sc.get('user'), sc.get('user'), directory))
        make_movies(directory)


def make_movies(directory):
    use_existing = settings.cluster.get('use_existing', True)
    if use_existing:
        return None
    sc = settings.cluster
    seekwatcher = '/home/%s/bin/seekwatcher' % sc.get('user')
    blktrace_dir = '%s/blktrace' % directory

    for device in range(sc.get('osds_per_node')):
        common.pdsh(settings.getnodes('osds'), 'cd %s;%s -t device%s -o device%s.mpg --movie' %
                    (blktrace_dir, seekwatcher, device, device)).communicate()
