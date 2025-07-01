#!/bin/sh
interface=eno2

verb="$1"

case "$verb" in 
  "enable")
    echo "++++ enable was chosen ++++"
    old_metric=100
    new_metric=50
    ;;
  "disable")
    echo "#### disable was chosen ####"
    old_metric=50
    new_metric=100
    ;;
  *)
    echo "!!!! nothing was chosen !!!!"
    old_metric=50
    new_metric=100
esac

echo "before:"
ip r sh default
echo ""

echo "deleting old one"
echo "ip r delete  default via 192.168.100.1 dev ${interface} proto dhcp src 192.168.100.51 metric ${old_metric} "
ip r delete  default via 192.168.100.1 dev ${interface} proto dhcp src 192.168.100.51 metric ${old_metric}
echo ""

sleep 2

echo "adding new one"
echo "ip r add     default via 192.168.100.1 dev ${interface} proto dhcp src 192.168.100.51 metric ${new_metric}"
ip r add     default via 192.168.100.1 dev ${interface} proto dhcp src 192.168.100.51 metric ${new_metric}
echo ""

echo "after:"
ip r sh default
echo ""

echo "new default ip: $(curl -s 4.icanhazip.com)"

