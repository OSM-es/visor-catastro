<script>
  import { locale } from '$lib/translations'

  export let value

	$: formattedNumber = Number(value).toLocaleString(locale, {
		notation: value > 9999 ? 'compact' : 'standard',
		compactDisplay: 'short'
	})
</script>

<span>{formattedNumber}</span>

<style>
	span {
		font-variant-numeric: tabular-nums;
	}
</style>
